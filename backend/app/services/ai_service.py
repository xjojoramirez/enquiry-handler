import json
import re
from typing import Any

import httpx

from app.config.settings import settings

SYSTEM_PROMPT = settings.system_prompt


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
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{settings.model_base_url.rstrip('/')}/chat/completions"
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

    return extract_json(content)
