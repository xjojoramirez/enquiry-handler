# Deployment

## Docker Compose

The project runs in three containers:

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| db | postgres:16 | 6102 | PostgreSQL database |
| backend | enquiry-handler-backend | 6101 | FastAPI application |
| frontend | enquiry-handler-frontend | 6100 | Nginx serving React SPA |

### Commands

```bash
# Full rebuild and start
docker compose up --build

# Start in background
docker compose up -d

# Rebuild single service
docker compose up -d --build backend

# View logs
docker compose logs -f backend

# Stop all
docker compose down
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | — | LLM provider API key |
| `MODEL_NAME` | deepseek-v4-flash | Model identifier |
| `MODEL_BASE_URL` | https://opencode.ai/zen/go/v1 | OpenAI-compatible API base |
| `DATABASE_URL` | postgresql+asyncpg://... | PostgreSQL connection |
