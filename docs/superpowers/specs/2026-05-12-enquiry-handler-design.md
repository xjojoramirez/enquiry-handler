# AI Enquiry Handler — Design Spec

## Overview

A lightweight AI-powered internal tool for Strata Management Consultants to process incoming client enquiries. Staff paste an enquiry → AI classifies it, assesses urgency, extracts entities, and drafts a suggested response → results displayed in a clean web UI.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  React SPA  │────▶│  FastAPI     │────▶│  LLM API         │
│  (Vite)     │◀────│  (uvicorn)   │◀────│  (configurable)  │
└─────────────┘     └──────┬───────┘     └──────────────────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    └──────────────┘
```

Three Docker containers orchestrated via Docker Compose:
- **frontend** — Nginx serving built React SPA
- **backend** — FastAPI (uvicorn)
- **db** — PostgreSQL 16 Alpine

## Backend (FastAPI)

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/classify` | Analyse enquiry, no persistence |
| `POST` | `/api/enquiries` | Analyse + persist to DB |
| `GET` | `/api/enquiries` | List all persisted enquiries |
| `GET` | `/api/enquiries/{id}` | Single enquiry detail |
| `GET` | `/api/enquiries/export` | JSON export for CRM integration |

### Response Shape

```json
{
  "id": "uuid",
  "original_text": "...",
  "classification": {
    "type": "support_request",
    "subtype": "maintenance",
    "confidence": 0.92,
    "explanation": "Clear language about a repair issue..."
  },
  "priority": "high",
  "summary": "Existing client reporting a maintenance issue in unit 4B.",
  "entities": { "client_name": "Acme Corp", "unit": "4B" },
  "recommended_team": "Maintenance",
  "suggested_response": "Thank you for reaching out...",
  "timestamp": "2026-05-12T10:30:00Z"
}
```

### AI Pipeline (single LLM call)

1. **Validate input** — empty/gibberish check (character diversity < 0.4 → early return)
2. **LLM call** — OpenAI-compatible API with configurable model + base URL
3. **Parse response** — expect JSON in a markdown code block; regex-extract if needed
4. **Return enriched result**
5. **Error fallback** — API failure → error classification; non-JSON → error classification

### Classification Types

| Type | Description |
|------|-------------|
| `new_client` | Prospective client enquiry |
| `support_request` | Existing client needs help |
| `complaint` | Dissatisfaction or issue |
| `general_question` | Non-specific or informational |

### Prompt Design

**System prompt:**
- Role definition as Strata Management Consultants AI assistant
- Task: classify, extract entities, assess urgency, draft response
- Strict JSON output schema specified in prompt
- Brief chain-of-thought step before answer
- One few-shot example per classification type

**Config** (`config.yaml`):
```yaml
model:
  name: deepseek-v4-flash
  base_url: https://api.opencode.ai/v1
classification_types:
  - new_client
  - support_request
  - complaint
  - general_question
webhook_url: ""
```

### Error Handling

- **Empty/gibberish** — pre-check, skip LLM, return `unprocessable` classification
- **API failure** — return error classification with service-unavailable message
- **Non-JSON response** — regex fallback; if still fails, error classification
- **Vague input** — LLM classifies as `general_question` with low confidence; response asks clarifying questions

## Database (PostgreSQL)

### Schema

```sql
CREATE TABLE enquiries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_text TEXT NOT NULL,
    classification JSONB NOT NULL,
    priority VARCHAR(20) NOT NULL,
    summary TEXT,
    entities JSONB,
    recommended_team VARCHAR(100),
    suggested_response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Index on `created_at` for history listing.

## Frontend (React + Vite)

### Views (single-page, no routing)

- **Input area** — textarea + "Analyse" button with loading spinner
- **Results panel** — classification badge, confidence bar, priority flag, summary, entities, recommended team, suggested response
- **History sidebar** — scrollable list; click to view detail
- **Detail view** — full card for selected past enquiry
- **Error/empty states** — graceful handling

### Components

- `App` — two-column layout (main + sidebar), state machine (idle/loading/result/error)
- `EnquiryForm` — textarea + submit
- `ClassificationBadge` — colored pill per type
- `ConfidenceMeter` — horizontal bar with percentage
- `ResultCard` — full analysis display
- `EnquiryHistory` — sidebar list
- `ErrorBanner` — dismissible error

Styled with Tailwind CSS.

## Deployment

### Docker Compose

```yaml
services:
  db:
    image: postgres:16-alpine
    env: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    volumes: pgdata

  backend:
    build: ./backend
    depends_on: db
    env: DATABASE_URL, API_KEY, MODEL_NAME, MODEL_BASE_URL

  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: backend
```

### Env vars (`.env`)

- `DATABASE_URL` — PostgreSQL connection string
- `API_KEY` — LLM provider API key
- `MODEL_NAME` — model identifier (default: deepseek-v4-flash)
- `MODEL_BASE_URL` — API base URL (default: https://api.opencode.ai/v1)

## Automation

- **Webhook** — if `webhook_url` set in config, POST each new enquiry to it
- **Export** — `GET /api/enquiries/export` for CRM data pull
- **Store abstraction** — `EnquiryStore` interface; swap Postgres for CRM API by implementing one class
