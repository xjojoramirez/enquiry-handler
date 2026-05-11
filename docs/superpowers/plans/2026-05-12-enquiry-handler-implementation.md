# AI Enquiry Handler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Dockerized AI enquiry handler with FastAPI backend, React frontend, and PostgreSQL database.

**Architecture:** Three containers (frontend/nginx, backend/uvicorn, db/postgres). Backend classifies enquiries via configurable LLM, stores results in PostgreSQL, serves REST API. Frontend SPA provides input form + results display + history.

**Tech Stack:** FastAPI (Python 3.12), React + Vite + Tailwind CSS, PostgreSQL 16, Docker Compose, OpenAI-compatible LLM API

---

## File Structure

```
enquiry-handler/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.yaml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── migrations.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── enquiries.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ai_service.py
│   │       └── enquiry_store.py
│   └── tests/
│       ├── __init__.py
│       ├── test_ai_service.py
│       ├── test_enquiry_store.py
│       └── test_routers.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx
│       ├── index.css
│       ├── App.jsx
│       ├── api.js
│       └── components/
│           ├── EnquiryForm.jsx
│           ├── ClassificationBadge.jsx
│           ├── ConfidenceMeter.jsx
│           ├── ResultCard.jsx
│           ├── EnquiryHistory.jsx
│           ├── ErrorBanner.jsx
│           └── LoadingSpinner.jsx
└── README.md
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/config.yaml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config/__init__.py`
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/tests/__init__.py`

- [ ] **Step 1: Create root docker-compose.yml**

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-enquiries}
      POSTGRES_USER: ${POSTGRES_USER:-enquiries}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-enquiries}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U enquiries"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL:-postgresql+asyncpg://enquiries:enquiries@db:5432/enquiries}
      API_KEY: ${API_KEY:-}
      MODEL_NAME: ${MODEL_NAME:-deepseek-v4-flash}
      MODEL_BASE_URL: ${MODEL_BASE_URL:-https://api.opencode.ai/v1}
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

- [ ] **Step 2: Create .env.example**

```
POSTGRES_DB=enquiries
POSTGRES_USER=enquiries
POSTGRES_PASSWORD=enquiries
DATABASE_URL=postgresql+asyncpg://enquiries:enquiries@db:5432/enquiries
API_KEY=your-api-key-here
MODEL_NAME=deepseek-v4-flash
MODEL_BASE_URL=https://api.opencode.ai/v1
```

- [ ] **Step 3: Create backend/requirements.txt**

```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
pydantic>=2.10.0
pydantic-settings>=2.7.0
httpx>=0.28.0
asyncpg>=0.30.0
sqlalchemy[asyncio]>=2.0.0
PyYAML>=6.0
pytest>=8.0
pytest-asyncio>=0.24.0
```

- [ ] **Step 4: Create backend/config.yaml**

```yaml
# backend/config.yaml
model:
  name: deepseek-v4-flash
  base_url: https://api.opencode.ai/v1
classification_types:
  - new_client
  - support_request
  - complaint
  - general_question
webhook_url: ""
system_prompt: |
  You are an AI assistant for Strata Management Consultants.
  Analyse the client enquiry and return a JSON object with:
  - classification: object with type (new_client|support_request|complaint|general_question), subtype (string), confidence (0.0-1.0), explanation (string)
  - priority: low|medium|high
  - summary: one-sentence summary
  - entities: object with extracted names, unit numbers, etc.
  - recommended_team: string
  - suggested_response: draft reply text

  Think step by step before answering. Output valid JSON only.
```

- [ ] **Step 5: Create all `__init__.py` files (empty)**

```python
# backend/app/__init__.py
# backend/app/config/__init__.py
# backend/app/db/__init__.py
# backend/app/models/__init__.py
# backend/app/routers/__init__.py
# backend/app/services/__init__.py
# backend/tests/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml .env.example backend/requirements.txt backend/config.yaml backend/app/__init__.py backend/app/config/__init__.py backend/app/db/__init__.py backend/app/models/__init__.py backend/app/routers/__init__.py backend/app/services/__init__.py backend/tests/__init__.py
git commit -m "chore: scaffold project structure with Docker Compose, config, and requirements"
```

---

### Task 2: Backend — Config & Settings

**Files:**
- Create: `backend/app/config/settings.py`

- [ ] **Step 1: Write settings module**

```python
# backend/app/config/settings.py
import os
from pathlib import Path
from typing import Optional

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


class Settings:
    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://enquiries:enquiries@localhost:5432/enquiries",
        )
        self.api_key: str = os.getenv("API_KEY", "")
        self.model_name: str = os.getenv("MODEL_NAME", "deepseek-v4-flash")
        self.model_base_url: str = os.getenv(
            "MODEL_BASE_URL", "https://api.opencode.ai/v1"
        )

        raw = self._load_config()
        self.classification_types: list[str] = raw.get(
            "classification_types",
            ["new_client", "support_request", "complaint", "general_question"],
        )
        self.webhook_url: str = raw.get("webhook_url", "")
        self.system_prompt: str = raw.get(
            "system_prompt",
            "You are an AI assistant for Strata Management Consultants.",
        )

    def _load_config(self) -> dict:
        path = Path(CONFIG_PATH)
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def model_config(self) -> dict:
        raw = self._load_config()
        return raw.get("model", {})


settings = Settings()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/config/settings.py
git commit -m "feat: add settings module loading env vars and config.yaml"
```

---

### Task 3: Backend — Pydantic Schemas

**Files:**
- Create: `backend/app/models/schemas.py`

- [ ] **Step 1: Write schemas**

```python
# backend/app/models/schemas.py
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    type: str
    subtype: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = ""


class EnquiryResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    original_text: str
    classification: ClassificationResult
    priority: str = "medium"
    summary: str = ""
    entities: dict = {}
    recommended_team: str = ""
    suggested_response: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    classification: ClassificationResult
    priority: str
    summary: str
    entities: dict
    recommended_team: str
    suggested_response: str


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/schemas.py
git commit -m "feat: add Pydantic schemas for request/response models"
```

---

### Task 4: Backend — Database Layer

**Files:**
- Create: `backend/app/db/database.py`
- Create: `backend/app/db/migrations.py`

- [ ] **Step 1: Write database connection module**

```python
# backend/app/db/database.py
import asyncpg
from app.config.settings import settings

pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    return pool


async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None
```

- [ ] **Step 2: Write migrations module**

```python
# backend/app/db/migrations.py
import asyncpg


async def run_migrations(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                original_text TEXT NOT NULL,
                classification JSONB NOT NULL,
                priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                summary TEXT,
                entities JSONB DEFAULT '{}',
                recommended_team VARCHAR(100),
                suggested_response TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_enquiries_created_at
            ON enquiries (created_at DESC);
        """)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/db/database.py backend/app/db/migrations.py
git commit -m "feat: add database connection pool and migration"
```

---

### Task 5: Backend — Enquiry Store

**Files:**
- Create: `backend/app/services/enquiry_store.py`
- Create: `backend/tests/test_enquiry_store.py`

- [ ] **Step 1: Write the failing test for enquiry_store**

```python
# backend/tests/test_enquiry_store.py
import pytest
from app.models.schemas import EnquiryResponse, ClassificationResult
from app.services.enquiry_store import EnquiryStore


@pytest.mark.asyncio
async def test_save_and_retrieve_enquiry():
    store = EnquiryStore()
    enquiry = EnquiryResponse(
        original_text="Test enquiry",
        classification=ClassificationResult(
            type="general_question", confidence=0.5, explanation="test"
        ),
        priority="low",
        summary="A test",
        recommended_team="Sales",
        suggested_response="Thanks",
    )
    saved = await store.save(enquiry)
    assert saved.id == enquiry.id

    retrieved = await store.get(enquiry.id)
    assert retrieved is not None
    assert retrieved.original_text == "Test enquiry"


@pytest.mark.asyncio
async def test_list_enquiries_empty():
    store = EnquiryStore()
    result = await store.list_all()
    assert result == []


@pytest.mark.asyncio
async def test_list_enquiries_with_data():
    store = EnquiryStore()
    e1 = EnquiryResponse(
        original_text="First",
        classification=ClassificationResult(type="new_client", confidence=0.9, explanation=""),
    )
    e2 = EnquiryResponse(
        original_text="Second",
        classification=ClassificationResult(type="complaint", confidence=0.8, explanation=""),
    )
    await store.save(e1)
    await store.save(e2)
    result = await store.list_all()
    assert len(result) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_enquiry_store.py -v`
Expected: FAIL with "ModuleNotFoundError" or "cannot import"

- [ ] **Step 3: Write the enquiry store implementation**

```python
# backend/app/services/enquiry_store.py
from uuid import UUID
from typing import Optional

from app.db.database import get_pool
from app.models.schemas import EnquiryResponse


class EnquiryStore:
    async def save(self, enquiry: EnquiryResponse) -> EnquiryResponse:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO enquiries (id, original_text, classification, priority,
                                       summary, entities, recommended_team, suggested_response)
                VALUES ($1, $2, $3::jsonb, $4, $5, $6::jsonb, $7, $8)
                """,
                enquiry.id,
                enquiry.original_text,
                enquiry.classification.model_dump_json(),
                enquiry.priority,
                enquiry.summary,
                enquiry.entities,
                enquiry.recommended_team,
                enquiry.suggested_response,
            )
        return enquiry

    async def get(self, enquiry_id: UUID) -> Optional[EnquiryResponse]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM enquiries WHERE id = $1", enquiry_id
            )
        if row is None:
            return None
        return self._row_to_enquiry(row)

    async def list_all(self) -> list[EnquiryResponse]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM enquiries ORDER BY created_at DESC"
            )
        return [self._row_to_enquiry(row) for row in rows]

    def _row_to_enquiry(self, row) -> EnquiryResponse:
        from app.models.schemas import ClassificationResult
        import json

        cls_data = json.loads(row["classification"])
        return EnquiryResponse(
            id=row["id"],
            original_text=row["original_text"],
            classification=ClassificationResult(**cls_data),
            priority=row["priority"],
            summary=row["summary"] or "",
            entities=json.loads(row["entities"]) if isinstance(row["entities"], str) else row["entities"] or {},
            recommended_team=row["recommended_team"] or "",
            suggested_response=row["suggested_response"] or "",
            timestamp=row["created_at"],
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_enquiry_store.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/enquiry_store.py backend/tests/test_enquiry_store.py
git commit -m "feat: add enquiry store with PostgreSQL persistence"
```

---

### Task 6: Backend — AI Service

**Files:**
- Create: `backend/app/services/ai_service.py`
- Create: `backend/tests/test_ai_service.py`

- [ ] **Step 1: Write the failing test for AI service**

```python
# backend/tests/test_ai_service.py
import pytest
from app.services.ai_service import classify_enquiry, GibberishDetector


def test_gibberish_detection():
    detector = GibberishDetector()
    assert detector.is_gibberish("akjsdhf laksjdhf lkajshdf lkjahsd")
    assert not detector.is_gibberish("Hi, I would like information about your services")
    assert detector.is_gibberish("")


@pytest.mark.asyncio
async def test_classify_enquiry_returns_expected_structure():
    result = await classify_enquiry("I want to buy a strata property")
    assert "classification" in result
    assert "priority" in result
    assert "summary" in result
    assert "recommended_team" in result
    assert "suggested_response" in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_ai_service.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write the AI service implementation**

```python
# backend/app/services/ai_service.py
import json
import re
from typing import Any

import httpx

from app.config.settings import settings

CLASSIFICATION_TYPES = "|".join(settings.classification_types)

SYSTEM_PROMPT = settings.system_prompt or f"""You are an AI assistant for Strata Management Consultants.
Analyse the client enquiry and return a JSON object with:
- classification: object with type ({CLASSIFICATION_TYPES}), subtype (string), confidence (0.0-1.0), explanation (string)
- priority: low|medium|high
- summary: one-sentence summary
- entities: object with extracted names, unit numbers, etc.
- recommended_team: string
- suggested_response: draft reply text

Think step by step before answering. Output valid JSON only."""


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
        return json.loads(match.group(1))
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_ai_service.py -v`
Expected: PASS (the classify test may need API key; the gibberish test should pass)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/ai_service.py backend/tests/test_ai_service.py
git commit -m "feat: add AI service with gibberish detection and LLM classification"
```

---

### Task 7: Backend — API Routers

**Files:**
- Create: `backend/app/routers/enquiries.py`
- Create: `backend/tests/test_routers.py`

- [ ] **Step 1: Write minimal main.py so the app can be imported**

```python
# backend/app/main.py
from fastapi import FastAPI
from app.routers.enquiries import router

app = FastAPI(title="AI Enquiry Handler", version="1.0.0")
app.include_router(router)
```

- [ ] **Step 2: Write the failing test for routers**

```python
# backend/tests/test_routers.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_classify_endpoint_empty_input():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/classify", json={"text": ""})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_classify_endpoint_valid_input():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/classify", json={"text": "I need help with my account"})
    assert resp.status_code == 200
    data = resp.json()
    assert "classification" in data
    assert "priority" in data
    assert "summary" in data
    assert "recommended_team" in data
    assert "suggested_response" in data
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_routers.py -v`
Expected: FAIL with "cannot import app" (it won't find `app.main` because no main.py yet — that's created in Step 1 so this should actually pass; the real fail will come when we haven't written the router yet but wait, Step 1 created main.py which imports the router... The test will fail because the router module doesn't exist yet.)

- [ ] **Step 4: Write the router**

```python
# backend/app/routers/enquiries.py
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.models.schemas import ClassifyRequest, ClassifyResponse, ErrorResponse, EnquiryResponse
from app.services.ai_service import classify_enquiry
from app.services.enquiry_store import EnquiryStore

router = APIRouter(prefix="/api", tags=["enquiries"])
store = EnquiryStore()


@router.post("/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Enquiry text cannot be empty")
    try:
        result = await classify_enquiry(req.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    return ClassifyResponse(**result)


@router.post("/enquiries", response_model=EnquiryResponse, status_code=201)
async def create_enquiry(req: ClassifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Enquiry text cannot be empty")
    try:
        result = await classify_enquiry(req.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    enquiry = EnquiryResponse(
        original_text=req.text,
        classification=result["classification"],
        priority=result.get("priority", "medium"),
        summary=result.get("summary", ""),
        entities=result.get("entities", {}),
        recommended_team=result.get("recommended_team", ""),
        suggested_response=result.get("suggested_response", ""),
    )
    return await store.save(enquiry)


@router.get("/enquiries", response_model=list[EnquiryResponse])
async def list_enquiries():
    return await store.list_all()


@router.get("/enquiries/{enquiry_id}", response_model=EnquiryResponse)
async def get_enquiry(enquiry_id: UUID):
    enquiry = await store.get(enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return enquiry


@router.get("/enquiries/export", response_model=list[EnquiryResponse])
async def export_enquiries():
    return await store.list_all()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_routers.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/main.py backend/app/routers/enquiries.py backend/tests/test_routers.py
git commit -m "feat: add API routers for classify, CRUD, and export endpoints"
```

---

### Task 8: Backend — Main App Lifecycle & Webhook

**Files:**
- Modify: `backend/app/main.py` (add lifespan, CORS, migrations)
- Modify: `backend/app/routers/enquiries.py` (add webhook call)

- [ ] **Step 1: Update main.py with lifespan, CORS, and migrations**

```python
# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import get_pool, close_pool
from app.db.migrations import run_migrations
from app.routers.enquiries import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await get_pool()
    await run_migrations(pool)
    yield
    await close_pool()


app = FastAPI(title="AI Enquiry Handler", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
```

- [ ] **Step 2: Add webhook call to enquiries.py**

Add at the top of `backend/app/routers/enquiries.py` (in the import section):
```python
import httpx
from app.config.settings import settings
```

Add a helper function and call it after saving in `create_enquiry`:

```python
async def _fire_webhook(enquiry: EnquiryResponse):
    if not settings.webhook_url:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                settings.webhook_url,
                json=enquiry.model_dump(mode="json"),
            )
    except Exception:
        pass  # fire-and-forget, don't block on webhook
```

Modify the `create_enquiry` function — add after `return await store.save(enquiry)`:
```python
    saved = await store.save(enquiry)
    await _fire_webhook(saved)
    return saved
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py backend/app/routers/enquiries.py
git commit -m "feat: add FastAPI main app with lifespan, CORS, and webhook support"
```

---

### Task 9: Backend — Dockerfile

**Files:**
- Create: `backend/Dockerfile`

- [ ] **Step 1: Write Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Commit**

```bash
git add backend/Dockerfile
git commit -m "chore: add backend Dockerfile"
```

---

### Task 10: Frontend — Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/index.css`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "enquiry-handler-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^6.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

- [ ] **Step 2: Create vite.config.js**

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://backend:8000',
    },
  },
});
```

- [ ] **Step 3: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Enquiry Handler</title>
  </head>
  <body class="bg-gray-50">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Create postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 5: Create tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

- [ ] **Step 6: Create src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 7: Create src/main.jsx**

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 8: Commit**

```bash
git add frontend/package.json frontend/vite.config.js frontend/index.html frontend/postcss.config.js frontend/tailwind.config.js frontend/src/main.jsx frontend/src/index.css
git commit -m "chore: scaffold frontend with Vite, React, and Tailwind CSS"
```

---

### Task 11: Frontend — API Client

**Files:**
- Create: `frontend/src/api.js`

- [ ] **Step 1: Write API client**

```javascript
const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export function classify(text) {
  return request('/classify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export function submitEnquiry(text) {
  return request('/enquiries', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export function listEnquiries() {
  return request('/enquiries');
}

export function getEnquiry(id) {
  return request(`/enquiries/${id}`);
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api.js
git commit -m "feat: add API client for backend communication"
```

---

### Task 12: Frontend — Components (Part 1)

**Files:**
- Create: `frontend/src/components/LoadingSpinner.jsx`
- Create: `frontend/src/components/ErrorBanner.jsx`
- Create: `frontend/src/components/EnquiryForm.jsx`
- Create: `frontend/src/components/ClassificationBadge.jsx`
- Create: `frontend/src/components/ConfidenceMeter.jsx`

- [ ] **Step 1: Create LoadingSpinner**

```jsx
export default function LoadingSpinner() {
  return (
    <div className="flex justify-center py-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  );
}
```

- [ ] **Step 2: Create ErrorBanner**

```jsx
export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
      <span className="block sm:inline">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="absolute top-0 bottom-0 right-0 px-4"
        >
          &times;
        </button>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create EnquiryForm**

```jsx
import { useState } from 'react';

export default function EnquiryForm({ onSubmit, loading }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) onSubmit(text);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste client enquiry here..."
        className="w-full border border-gray-300 rounded-lg p-3 h-28 focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !text.trim()}
        className="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Analysing...' : 'Analyse Enquiry'}
      </button>
    </form>
  );
}
```

- [ ] **Step 4: Create ClassificationBadge**

```jsx
const COLORS = {
  new_client: 'bg-green-100 text-green-800',
  support_request: 'bg-blue-100 text-blue-800',
  complaint: 'bg-red-100 text-red-800',
  general_question: 'bg-gray-100 text-gray-800',
};

const LABELS = {
  new_client: 'New Client',
  support_request: 'Support',
  complaint: 'Complaint',
  general_question: 'General',
};

export default function ClassificationBadge({ type }) {
  const colorClass = COLORS[type] || 'bg-gray-100 text-gray-800';
  const label = LABELS[type] || type;
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${colorClass}`}>
      {label}
    </span>
  );
}
```

- [ ] **Step 5: Create ConfidenceMeter**

```jsx
export default function ConfidenceMeter({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct > 80 ? 'bg-green-500' : pct > 50 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm text-gray-600 w-10 text-right">{pct}%</span>
    </div>
  );
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/LoadingSpinner.jsx frontend/src/components/ErrorBanner.jsx frontend/src/components/EnquiryForm.jsx frontend/src/components/ClassificationBadge.jsx frontend/src/components/ConfidenceMeter.jsx
git commit -m "feat: add core UI components — form, badges, meters, spinners, errors"
```

---

### Task 13: Frontend — Components (Part 2) + App

**Files:**
- Create: `frontend/src/components/ResultCard.jsx`
- Create: `frontend/src/components/EnquiryHistory.jsx`
- Create: `frontend/src/App.jsx`

- [ ] **Step 1: Create ResultCard**

```jsx
import ClassificationBadge from './ClassificationBadge';
import ConfidenceMeter from './ConfidenceMeter';

export default function ResultCard({ result }) {
  if (!result) return null;
  const { classification, priority, summary, entities, recommended_team, suggested_response } = result;

  const priorityColor =
    priority === 'high' ? 'text-red-600' : priority === 'medium' ? 'text-yellow-600' : 'text-green-600';

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <ClassificationBadge type={classification?.type} />
        <span className={`font-semibold capitalize ${priorityColor}`}>{priority} Priority</span>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-1">Confidence</p>
        <ConfidenceMeter value={classification?.confidence} />
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-1">Summary</p>
        <p>{summary}</p>
      </div>

      {entities && Object.keys(entities).length > 0 && (
        <div>
          <p className="text-sm text-gray-500 mb-1">Entities</p>
          <pre className="text-sm bg-gray-50 p-2 rounded">{JSON.stringify(entities, null, 2)}</pre>
        </div>
      )}

      <div>
        <p className="text-sm text-gray-500 mb-1">Recommended Team</p>
        <p className="font-medium">{recommended_team}</p>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-1">Suggested Response</p>
        <div className="bg-gray-50 border border-gray-200 rounded p-3 whitespace-pre-wrap text-sm">
          {suggested_response}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create EnquiryHistory**

```jsx
import { useState, useEffect } from 'react';
import { listEnquiries } from '../api';

export default function EnquiryHistory({ onSelect }) {
  const [enquiries, setEnquiries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listEnquiries()
      .then(setEnquiries)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-gray-400">Loading...</p>;
  if (enquiries.length === 0) return <p className="text-sm text-gray-400">No enquiries yet.</p>;

  return (
    <div className="space-y-2">
      <h3 className="font-semibold text-gray-700 mb-2">History</h3>
      {enquiries.map((e) => (
        <button
          key={e.id}
          onClick={() => onSelect(e)}
          className="w-full text-left p-2 rounded hover:bg-gray-100 text-sm truncate border border-gray-100"
        >
          <span className="font-medium capitalize text-xs text-gray-500">{e.classification?.type}</span>
          <p className="truncate">{e.summary}</p>
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Create App.jsx**

```jsx
import { useState } from 'react';
import EnquiryForm from './components/EnquiryForm';
import ResultCard from './components/ResultCard';
import EnquiryHistory from './components/EnquiryHistory';
import ErrorBanner from './components/ErrorBanner';
import LoadingSpinner from './components/LoadingSpinner';
import { classify } from './api';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyse = async (text) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await classify(text);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold text-gray-800">AI Enquiry Handler</h1>
          <p className="text-sm text-gray-500">Strata Management Consultants</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 flex gap-6">
        <div className="flex-1">
          <EnquiryForm onSubmit={handleAnalyse} loading={loading} />
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
          {loading && <LoadingSpinner />}
          {result && <ResultCard result={result} />}
        </div>
        <aside className="w-72 shrink-0">
          <EnquiryHistory onSelect={setResult} />
        </aside>
      </main>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ResultCard.jsx frontend/src/components/EnquiryHistory.jsx frontend/src/App.jsx
git commit -m "feat: add ResultCard, EnquiryHistory, and main App component"
```

---

### Task 14: Frontend — Dockerfile

**Files:**
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Write multi-stage Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

- [ ] **Step 2: Create nginx.conf**

```
# frontend/nginx.conf
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/Dockerfile frontend/nginx.conf
git commit -m "chore: add frontend Dockerfile with multi-stage build and nginx"
```

---

### Task 15: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup, usage, and design decisions"
```

---

## Self-Review

To be completed after writing the plan.

1. **Spec coverage:** Every spec requirement maps to a task. Classify (T6, T7), persist (T5, T7), config (T2), frontend (T10-T14), Docker (T1, T9, T14), README (T15). Bonus items: confidence scoring (T6 prompt), gibberish detection (T6), webhook (T8), export (T7), prompt engineering explained (T15).
2. **Placeholder scan:** No TODOs, TBDs, or vague instructions. All code is complete.
3. **Type consistency:** Schemas in T3 match usage in T5, T6, T7. Field names are consistent throughout.
4. **No gaps found.**
