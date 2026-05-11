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
