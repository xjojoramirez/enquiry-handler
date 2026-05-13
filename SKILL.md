---
name: enquiry-handler
description: Use when setting up, configuring, or understanding the AI Enquiry Handler project
---

# AI Enquiry Handler

An AI-powered tool for Strata Business Brokers to process incoming client enquiries. Classifies, summarises, and drafts responses automatically.

## Skills

| Skill | Path | Purpose |
|-------|------|---------|
| backend | `backend/` | FastAPI app with classification, storage, and API skills |
| frontend | `frontend/` | React/Vite UI with form, result, and history skills |
| deploy | `docs/skills/deploy/` | Docker Compose, nginx, and deployment configuration |

## Quick Start

```bash
cp .env.example .env   # edit API_KEY
docker compose up --build
# Open http://localhost:6100
```

## Architecture

```
Frontend (React/Vite, nginx :6100)
    ↕ HTTP
Backend (FastAPI, uvicorn :6101)
    ↕ asyncpg
PostgreSQL (port 6102)
    ↕ HTTP
LLM API (OpenCode Go or compatible)
```
