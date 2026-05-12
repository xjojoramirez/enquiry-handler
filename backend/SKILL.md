---
name: backend
description: Use when working with the FastAPI backend service for enquiry processing
---

# Backend

## Overview
FastAPI application that classifies strata management enquiries via LLM, persists results to PostgreSQL, and serves the REST API.

## Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| classification | `app/skills/classification/` | AI-driven enquiry analysis (LLM call, gibberish detection, JSON parsing) |
| storage | `app/skills/storage/` | PostgreSQL persistence (pool management, migrations, CRUD) |
| api | `app/skills/api/` | FastAPI router endpoints (/classify, /enquiries) |

## Quick Reference

```bash
# Run tests
cd backend && python -m pytest

# Start dev server
uvicorn app.main:app --host 0.0.0.0 --port 6101 --reload
```
