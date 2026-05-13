# AI Enquiry Handler

An AI-powered enquiry triage tool built for **Strata Business Brokers**, Australia's specialist broker for strata management business sales.

The user pastes a raw client email/enquiry into the web UI. The system sends it to an LLM (with a company-specific system prompt), which analyses the enquiry and returns a structured assessment — including classification, priority, summary, and a draft response ready to send. No external email or CRM integration required for core usage.

## Usage

1. Paste a client enquiry (email text) into the text area
2. Click **"Analyse Enquiry"** — the system sends it to the LLM for analysis
3. Review the structured result:
   - **Classification** — type (new\_client / support\_request / complaint / general\_question) and subtype describing the next action
   - **Confidence** — how certain the LLM is about the classification (0–100%)
   - **Priority** — low / medium / high
   - **Summary** — one-sentence recap of the client's situation
   - **Entities** — extracted names, addresses, dates, amounts
   - **Recommended team** — which internal team should handle it
   - **Suggested response** — a complete, professional email draft ready to send
4. Past analyses appear in the history panel on the left; click any to revisit

## How the System Prompt Matches Company Information

The system prompt (in `backend/config.yaml`) embeds Strata Business Brokers' real business details directly into the LLM's instructions:

- **Company identity** — name, tagline ("Bridging opportunity and success in strata management business sales"), specialisation (exclusively strata), director (David Lin)
- **Services** — the six core service lines (valuation, marketing, negotiation, due diligence, transaction management, end-to-end service)
- **Differentiators** — unrivalled buyer network, nationwide reach, confidential process, hands-on service
- **Analysis process** — step-by-step instructions that mirror how a human broker would triage an enquiry: identify buy/sell/valuation intent, note urgency signals, reason about the classification, suggest a concrete next action

This ensures every response is framed in SBB's voice, references the correct services, and produces output that staff can act on without editing.

## Quick Start

1. **Clone and enter the project**
2. **Copy environment file** — `cp .env.example .env` and edit `API_KEY` with your LLM provider key
3. **Start all services** — `docker compose up --build`
4. **Open** — http://localhost in your browser

## Configuration

Edit `backend/config.yaml` to customise:
- Model name and API base URL
- Classification types
- System prompt
- Webhook URL (for CRM/email integration)

Environment variables (`.env`):
- `API_KEY` — LLM provider API key
- `MODEL_NAME` — model identifier (default: deepseek-v4-flash)
- `MODEL_BASE_URL` — API base URL
- `DATABASE_URL` — PostgreSQL connection string

## Architecture

```
Frontend (React/Vite) → Backend (FastAPI) → LLM API (configurable)
                         ↓
                      PostgreSQL
```

Three Docker containers: frontend (nginx), backend (uvicorn), database (PostgreSQL 16).

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/classify | Analyse enquiry (no persistence) |
| POST | /api/enquiries | Analyse + persist to database |
| GET | /api/enquiries | List all processed enquiries |
| GET | /api/enquiries/{id} | Get single enquiry detail |
| GET | /api/enquiries/export | List all enquiries (alias) |

## Design Decisions

- **Single LLM call**: Rather than a multi-stage pipeline, one well-prompted call returns all structured data. Faster and cheaper, with prompt engineering to ensure quality.
- **Gibberish detection**: Pre-checks input character diversity before hitting the API — saves cost on clearly invalid input.
- **Configurable prompt**: The system prompt lives in `config.yaml`, making it easy to iterate without code changes.
- **Docker Compose**: One command to spin up the full stack. Suitable for both local dev and demo deployment.
- **Webhook**: Optional fire-and-forget POST to an external URL — shows how this could plug into a CRM or email system.

## Bonus Features

- Confidence scoring via LLM self-assessment
- Gibberish/vague input handling before API call
- Webhook integration for automation
- Export endpoint for CRM data pull
- Configurable model, prompt, and classification types
