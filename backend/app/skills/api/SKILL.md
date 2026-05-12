---
name: api
description: Use when defining or modifying REST API endpoints for the enquiry handler
---

# API

## Overview
FastAPI router exposing endpoints for enquiry classification, persistence, retrieval, and export.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/classify | Analyse enquiry (no persistence) |
| POST | /api/enquiries | Analyse + persist to database |
| GET | /api/enquiries | List all processed enquiries |
| GET | /api/enquiries/{id} | Get single enquiry detail |
| GET | /api/enquiries/export | Export all enquiries as JSON |

## Dependencies
- `app.skills.classification` — classify_enquiry, schemas
- `app.skills.storage` — EnquiryStore
