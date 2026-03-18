from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


def build_candidate_payload() -> dict[str, str]:
    return {
        "name": "Abner Final Test",
        "email": f"abner.final+{uuid4().hex}@example.com",
        "exam_focus": "Python Expert",
    }


async def test_create_candidate(client):
    payload = build_candidate_payload()

    response = await client.post("/api/v1/candidates/", json=payload)

    assert response.status_code == 201
    assert response.json()["name"] == "Abner Final Te"


async def test_list_candidates(client):
    create_response = await client.post(
        "/api/v1/candidates/",
        json=build_candidate_payload(),
    )

    assert create_response.status_code == 201

    response = await client.get("/api/v1/candidates/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
