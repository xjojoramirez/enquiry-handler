# AI Enquiry Handler — System Overview

## Confidence Scoring

The LLM self-assesses confidence. The prompt instructs it to return a `confidence` field (0.0–1.0) inside the `classification` object. The backend passes this through without modification. It is purely the model's own judgement — no ensemble, no calibration. The frontend displays it as a percentage bar.

## Prompt Engineering

The system prompt lives in `backend/config.yaml` and has three layers:

**Security directives** — hard-coded rules that forbid following instructions in the enquiry, revealing the prompt, or breaking JSON output. Injected enquiries triggering these get classified as `"injection_attempt"` with `confidence: 0.0`.

**Company context** — Strata Business Brokers' identity, services, differentiators. Every response is framed in their voice, referencing correct services.

**Analysis process & output format** — step-by-step triage reasoning (identify intent, note urgency, classify, explain, draft response), with an exact JSON schema. `temperature: 0` ensures deterministic output.

**Design rationale:** Single well-prompted LLM call instead of a multi-stage pipeline — faster, cheaper, and the explanation field captures the chain-of-thought reasoning.

## Error Handling (Vague/Nonsensical Input)

Three defense layers in `backend/app/skills/classification/ai_service.py`:

1. **Gibberish detection** — checks character diversity ratio; if unique chars > 85% of total length, it is likely random keystrokes → returns rejection with `confidence: 0.0`, subtype `"unprocessable"`.

2. **Prompt injection detection** — 8 regex patterns (`"ignore your instructions"`, `"you are now"`, `"new role"`, etc.). If 3+ patterns match, the input is rejected outright. 1–2 matches get redacted and proceed with a warning.

3. **AI/parsing fallback** — if the LLM call fails (timeout, network error) or returns non-JSON, it falls back to a safe default response. If the AI itself flags an `injection_attempt` subtype, that is also rejected.

The rejection response returns safe defaults: `"Could not process the enquiry."` with subtype `"unprocessable"` and `confidence: 0.0`.

## Automation Potential

The architecture supports several integration points:

- **Webhook** — every persisted enquiry fires a POST to a configurable `webhook_url` in `config.yaml`. Payload includes the full `EnquiryResponse` (classification, summary, entities, suggested response). Fire-and-forget with 5s timeout.

- **Export endpoint** (`GET /api/enquiries/export`) — returns all enquiries as JSON, ready for CRM data pulls.

- **API-first design** — all endpoints are RESTful. An email system could POST incoming emails to `/api/enquiries`, and a CRM could poll/consume the webhook or export endpoint. The frontend is purely a reference UI.
