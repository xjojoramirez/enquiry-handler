# AI Enquiry Handler

An AI-powered tool for Strata Management Consultants to process incoming client enquiries. Classifies, summarises, and drafts responses automatically.

## Quick Start

1. **Clone and enter the project**
2. **Copy environment file** — `cp .env.example .env` and edit `API_KEY` with your LLM provider key
3. **Start all services** — `docker compose up --build`
4. **Open** — http://localhost in your browser

## Usage

1. Paste a client enquiry into the text area
2. Click "Analyse Enquiry"
3. View the classification, confidence, priority, summary, and suggested response
4. Past analyses appear in the sidebar history

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
| GET | /api/enquiries/export | Export all enquiries as JSON |

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
