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
    re.compile(r"\bforget\b", re.IGNORECASE),
    re.compile(r"\bdisregard\s+(?:(?:your|previous|all|the)\s+)*(?:instructions?|prompt|rules?)\b", re.IGNORECASE),
    re.compile(r"\bdisregard\b", re.IGNORECASE),
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


def extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in response")


async def classify_enquiry(text: str) -> dict[str, Any]:
    detector = GibberishDetector()
    if detector.is_gibberish(text):
        return {
            "classification": {
                "type": "general_question",
                "subtype": "unprocessable",
                "confidence": 0.0,
                "explanation": "Input could not be understood.",
            },
            "priority": "low",
            "summary": "Unprocessable enquiry.",
            "entities": {},
            "recommended_team": "General",
            "suggested_response": "I'm sorry, I couldn't understand your enquiry. Could you please rephrase it?",
        }

    text = sanitize_input(text)

    key = hashlib.sha256(text.encode()).hexdigest()
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
            {"role": "user", "content": text},
        ],
        "temperature": 0,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        url = f"{settings.model_base_url.rstrip('/')}/chat/completions"
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

    result = extract_json(content)
    _cache[key] = result
    return result
