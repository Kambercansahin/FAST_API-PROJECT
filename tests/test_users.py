import pytest

from httpx import AsyncClient
from tests.conftest import auth_header,create_test_user,login_user


#check validation error when required fields are missing
@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    #test validation error when email and password are missing
    response = await client.post("/api/users",
        json={
            "username": "testkullanıcısı",
        },
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


## Test Create User Duplicate Email
@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@example.com",#our default e-mail - "test@example.com" we are using again here
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email sistemde mevcut"

## Test Create User Success
@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    #create a new user
    response = await client.post(
        "/api/users",
        json={
            "username": "new_user",
            "email": "new@example.com",
            "password": "word1234",
        },
    )
    # if response ==201
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_user" #new username
    assert data["email"] == "new@example.com" # new email
    assert "id" in data # if id  in data
    assert "image_path" in data # if image_path in data
    assert "password" not in data #ensure sensitive password data is not exposed in the response
    assert "password_hash" not in data #ensure sensitive password data is not exposed in the response