import hashlib
import json
import logging
import re
from typing import Any

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = settings.system_prompt
_cache: dict[str, dict[str, Any]] = {}


class GibberishDetector:
    def is_gibberish(self, text: str) -> bool:
        if not text or not text.strip():
            return True
        clean = re.sub(r"\s+", "", text)
        if len(clean) < 5:
            return True
        unique_chars = len(set(clean.lower()))
        ratio = unique_chars / len(clean)
        return ratio > 0.85


def sanitize_input(text: str) -> str:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


_INJECTION_PATTERNS = [
    re.compile(r"\bignore\s+(?:(?:your|previous|all|the)\s+)*(?:instructions?|prompt|system)\b", re.IGNORECASE),
    re.compile(r"\bforget\s+(?:(?:your|previous|all|the)\s+)*(?:instructions?|prompt|role|rules?)\b", re.IGNORECASE),
    re.compile(r"\bdisregard\s+(?:(?:your|previous|all|the)\s+)*(?:instructions?|prompt|rules?)\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
    re.compile(r"\bpretend\s+you\s+are\b", re.IGNORECASE),
    re.compile(r"\broleplay\s+as\b", re.IGNORECASE),
    re.compile(r"\boverride\s+(?:(?:your|previous|the)\s+)*(?:instructions?|prompt|rules?)\b", re.IGNORECASE),
    re.compile(r"\bnew\s+role\b", re.IGNORECASE),
]

_SEVERE_THRESHOLD = 3


def sanitize_prompt_injection(text: str) -> tuple[str, int]:
    count = 0
    for pattern in _INJECTION_PATTERNS:
        matches = pattern.findall(text)
        count += len(matches)
        text = pattern.sub("[redacted]", text)
    return text, count


_LEAKAGE_PATTERNS = [
    re.compile(r"\bsystem\s+prompt\b", re.IGNORECASE),
    re.compile(r"\bENQUIRY\s+BEGIN\b"),
    re.compile(r"\bENQUIRY\s+END\b"),
    re.compile(r"\bmy\s+instructions?\b", re.IGNORECASE),
    re.compile(r"\byour\s+instructions?\b", re.IGNORECASE),
    re.compile(r"\breveal(?:ing)?\s+my\b", re.IGNORECASE),
    re.compile(r"\bSECRET\b"),
]

_SAFE_DEFAULT_RESPONSE = "This email content relates to an enquiry, support request, or general question."

_SAFE_DEFAULT_CLASSIFICATION = {
    "type": "general_question",
    "subtype": "unprocessable",
    "confidence": 0.0,
    "explanation": "Could not process the enquiry.",
}


def _scrub_field(text: str) -> str:
    for pattern in _LEAKAGE_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text


def scrub_response(result: dict[str, Any]) -> dict[str, Any]:
    leaked = False
    for field in ("suggested_response", "summary"):
        if field in result:
            original = result[field]
            scrubbed = _scrub_field(original)
            if scrubbed != original:
                result[field] = scrubbed
                leaked = True
    if "classification" in result and isinstance(result["classification"], dict):
        for subfield in ("explanation",):
            if subfield in result["classification"]:
                original = result["classification"][subfield]
                scrubbed = _scrub_field(original)
                if scrubbed != original:
                    result["classification"][subfield] = scrubbed
                    leaked = True
    if leaked:
        logger.warning("Potential system prompt leakage in output")
    return result


def extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in response")


def _rejection_response() -> dict[str, Any]:
    return {
        "classification": {
            "type": "general_question",
            "subtype": "unprocessable",
            "confidence": 0.0,
            "explanation": "Could not process the enquiry.",
        },
        "priority": "low",
        "summary": "Could not process enquiry.",
        "entities": {},
        "recommended_team": "General",
        "suggested_response": _SAFE_DEFAULT_RESPONSE,
    }


def _format_enquiry(text: str) -> str:
    return f"---ENQUIRY BEGIN---\n{text}\n---ENQUIRY END---"


async def classify_enquiry(text: str) -> dict[str, Any]:
    detector = GibberishDetector()
    if detector.is_gibberish(text):
        return _rejection_response()

    text = sanitize_input(text)
    sanitized, injection_count = sanitize_prompt_injection(text)

    if injection_count >= _SEVERE_THRESHOLD:
        logger.warning("Prompt injection attempt: severe — rejected input")
        return _rejection_response()

    if injection_count > 0:
        logger.warning("Prompt injection attempt: minor neutralization (%d pattern(s))", injection_count)

    formatted = _format_enquiry(sanitized)

    key = hashlib.sha256(formatted.encode()).hexdigest()
    if key in _cache:
        return _cache[key]

    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": formatted},
        ],
        "temperature": 0,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            url = f"{settings.model_base_url.rstrip('/')}/chat/completions"
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error("AI service error: %s", e)
        return _rejection_response()

    try:
        result = extract_json(content)
    except (ValueError, json.JSONDecodeError):
        logger.warning("AI response was not valid JSON, returning fallback")
        return _rejection_response()

    if isinstance(result.get("classification"), dict):
        subtype = result["classification"].get("subtype", "")
        if subtype == "injection_attempt":
            logger.warning("AI detected injection attempt in output")
            return _rejection_response()

    result = scrub_response(result)
    _cache[key] = result
    return result
