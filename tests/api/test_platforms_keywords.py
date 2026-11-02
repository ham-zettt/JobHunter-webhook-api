from __future__ import annotations


async def test_platforms_endpoint(client, auth_headers):
    response = await client.get("/api/v1/platforms", headers=auth_headers)
    assert response.status_code == 200
    platforms = {p["platform"]: p for p in response.json()}
    assert set(platforms) == {
        "jobstreet",
        "glints",
        "kalibrr",
        "dealls",
        "kitalulus",
        "linkedin",
        "pintarnya",
    }
    assert platforms["linkedin"]["requires_auth"] is True
    assert platforms["linkedin"]["auth_state"] in ("missing", "expired", "valid")


async def test_keyword_crud(client, auth_headers):
    created = await client.post(
        "/api/v1/keywords",
        json={
            "type": "include",
            "term": "Rust Engineer",
            "strength": "strong",
            "role_category": "backend",
        },
        headers=auth_headers,
    )
    assert created.status_code == 201
    rule = created.json()
    assert rule["term"] == "rust engineer"
    assert rule["source"] == "user"

    listed = await client.get("/api/v1/keywords?type=include", headers=auth_headers)
    assert any(r["id"] == rule["id"] for r in listed.json())

    patched = await client.patch(
        f"/api/v1/keywords/{rule['id']}", json={"is_active": False}, headers=auth_headers
    )
    assert patched.json()["is_active"] is False

    deleted = await client.delete(f"/api/v1/keywords/{rule['id']}", headers=auth_headers)
    assert deleted.status_code == 204

    missing = await client.delete(f"/api/v1/keywords/{rule['id']}", headers=auth_headers)
    assert missing.status_code == 404


async def test_keyword_validation(client, auth_headers):
    response = await client.post(
        "/api/v1/keywords",
        json={
            "type": "include",
            "term": "x",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_reseed(client, auth_headers):
    response = await client.post("/api/v1/keywords/reseed", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["keywords"] > 0
    again = await client.post("/api/v1/keywords/reseed", headers=auth_headers)
    assert again.json()["keywords"] > 0
