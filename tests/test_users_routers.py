
from fastapi import FastAPI, APIRouter, HTTPException

import pytest
from httpx import AsyncClient

app = FastAPI()


@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/api") as client:
        response = await client.post("/session/", data={"username": "username", "password": "string"})
        print(response.json())
        assert response.status_code == 200
        # assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_refresh_token():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/session/")
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_signup():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/users/", json={"email": "test@example.com", "password": "testpass"})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_by_name_or_id():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/1")
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_all_users():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/all")
        assert response.status_code == 200
        assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_update_user_role():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch("/users/1/role", json={"new_role": "admin"})
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

@pytest.mark.asyncio
async def test_ban_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch("/users/1/ban")
        assert response.status_code == 200
        assert response.json()["banned"] == True

@pytest.mark.asyncio
async def test_unban_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch("/users/1/unban")
        assert response.status_code == 200
        assert response.json()["banned"] == False

@pytest.mark.asyncio
async def test_read_self_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/profile/")
        assert response.status_code == 200
        assert "email" in response.json()

@pytest.mark.asyncio
async def test_modify_self_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/profile/", json={"username": "newusername"})
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"

@pytest.mark.asyncio
async def test_read_user_photos():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/1/photos")
        assert response.status_code == 200
        assert "photos" in response.json()
