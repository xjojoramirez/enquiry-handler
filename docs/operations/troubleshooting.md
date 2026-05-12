# Troubleshooting

## Backend won't start (ConnectionRefused on DB)
The DB container may still be initializing. Docker Compose waits for the health check, but if the backend crashes immediately, run:
```bash
docker compose logs backend
```
If it shows `ConnectionRefusedError`, the DB wasn't ready. Run:
```bash
docker compose up -d --force-recreate backend
```

## LLM API returns 502 / "AI service error"
- Check `API_KEY` in `.env` is valid
- Check `MODEL_BASE_URL` points to a working OpenAI-compatible endpoint
- Check network connectivity from inside the container:
```bash
docker compose exec backend curl -s <model_base_url>/chat/completions
```
- The LLM call may timeout — try again (cache serves after first success)
