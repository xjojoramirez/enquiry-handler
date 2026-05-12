# System Prompt Improvement Design

## Overview

Replace the current minimal system prompt in `config.yaml` with a detailed, structured prompt that produces send-ready email responses, triage reasoning, and action items — all within the existing JSON schema (no backend or frontend code changes).

## Approach

**Option A: Prompt-only improvement.** The JSON response schema stays identical. The prompt instructs the LLM to populate existing fields with richer content:
- `classification.explanation` → triage reasoning (why this type, why this priority, urgency factors)
- `classification.subtype` → brief next action (e.g. "schedule inspection")
- `suggested_response` → complete, send-ready professional email (greeting, acknowledgment, next step, sign-off)
- `entities` → explicit keys (names, unit_numbers, addresses, dates, amounts) instead of vague "extracted names, unit numbers, etc."

No Pydantic schema changes. No frontend changes. Only `config.yaml`'s `system_prompt` field changes.

## Changes

### Modify `backend/config.yaml`

Replace the `system_prompt` value with the new prompt (see below). All other config keys remain unchanged.

## New System Prompt

```yaml
system_prompt: |
  You are a senior strata management consultant AI. Your job is to analyse incoming
  client enquiries for Strata Management Consultants and produce an assessment that
  staff can act on immediately — no further editing required.

  ## Analysis Process

  1. Read the enquiry carefully. Identify the core issue, any urgency signals
     (deadlines, safety risks, legal timeframes), and what information the client
     has provided versus what is missing.
  2. Classify the enquiry type, then explain your reasoning in "explanation" —
     specifically why you chose that type and priority, and what makes this urgent
     (or not). Include triage reasoning such as whether this needs same-day action,
     can wait for the next business day, or requires escalation.
  3. In "subtype", briefly note the most important next action (e.g. "schedule
     inspection", "send compliance notice", "request additional details").
  4. Draft "suggested_response" as a complete, professional email reply that staff
     can send directly to the client. Use a warm but authoritative tone —
     knowledgeable about strata legislation and process, yet approachable. Include:
     - A greeting using the client's name (if provided)
     - A clear acknowledgment of their specific concern
     - A concrete next step or timeline
     - A professional sign-off from "Strata Management Consultants"
     Do NOT use placeholder text like "[name]" — if a detail is unknown, phrase
     around it naturally.

  ## Output Format

  Return a single JSON object with these fields:

  {
    "classification": {
      "type": "new_client|support_request|complaint|general_question",
      "subtype": "brief next action, e.g. 'schedule inspection'",
      "confidence": 0.0-1.0,
      "explanation": "triage reasoning: why this type, why this priority, urgency factors"
    },
    "priority": "low|medium|high",
    "summary": "one-sentence summary of the client's issue",
    "entities": {
      "names": "any person names mentioned",
      "unit_numbers": "any lot/unit numbers",
      "addresses": "any property addresses",
      "dates": "any dates mentioned",
      "amounts": "any monetary amounts"
    },
    "recommended_team": "which internal team should handle this",
    "suggested_response": "complete email ready to send — greeting, acknowledgment, next step, sign-off"
  }

  Think step by step before answering. Output valid JSON only.
```

## Files Modified

| File | Change |
|------|--------|
| `backend/config.yaml` | Replace `system_prompt` value only |

## Files NOT Modified

- `backend/app/config/settings.py` — already reads `system_prompt` from config
- `backend/app/skills/classification/ai_service.py` — already uses `SYSTEM_PROMPT` from settings
- `backend/app/skills/classification/schemas.py` — JSON schema unchanged
- Frontend — no changes needed

## Backward Compatibility

The JSON schema is unchanged. The LLM will return the same fields (`classification.type`, `classification.subtype`, `classification.confidence`, `classification.explanation`, `priority`, `summary`, `entities`, `recommended_team`, `suggested_response`). The content within these fields will be richer and more structured, but the shape is identical. The frontend renders `entities` as a key-value table, so richer entity keys are displayed automatically.