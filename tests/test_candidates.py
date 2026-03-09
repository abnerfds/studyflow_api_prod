from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_candidate(client):
    payload = {
        "name": "Abner Final Test",
        "email": f"abner.final+{uuid4().hex}@example.com",
        "exam_focus": "Python Expert",
    }

    response = await client.post("/api/v1/candidates/", json=payload)

    assert response.status_code == 201
    assert response.json()["name"] == "Abner Final Test"


async def test_list_candidates(client):
    response = await client.get("/api/v1/candidates/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Como rodamos o POST antes, a lista deve ter conteúdo
    assert len(data) > 0
