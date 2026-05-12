# Architecture Overview

```
User Browser
    │
    ▼ http://localhost:6100
┌──────────────────────┐
│  Frontend (nginx)    │
│  - EnquiryForm       │
│  - ResultCard        │
│  - EnquiryHistory    │
└──────┬───────────────┘
       │ /api/* proxy
       ▼ http://backend:6101
┌──────────────────────┐
│  Backend (uvicorn)   │
│  - classification    │──→ LLM API (OpenCode Go)
│  - storage           │──→ PostgreSQL :6102
│  - api               │
└──────────────────────┘
```

## Data Flow

1. User pastes enquiry text → clicks Analyse
2. Frontend POSTs to `/api/classify`
3. Backend checks gibberish → if passes, calls LLM
4. LLM returns structured JSON → parsed and returned
5. For `/api/enquiries`: result is also persisted to PostgreSQL
6. Frontend displays result in ResultCard
