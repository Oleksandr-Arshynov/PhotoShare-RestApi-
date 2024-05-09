import pytest
from src.database.db import SessionLocal
from src.auth.dependencies_auth import auth_service
from src.schemas import schemas_auth
from src.tests.conftest import client




@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_user(db, client):
    # Create a new user through the API
    body = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "test_password",
    }
    response = client.post("/api/auth/signup", json=body)
    assert response.status_code == 201

def test_login_user(db, client):
    # Create a new user through the API
    user_data = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "test_password",
    }
    client.post("/api/auth/signup", json=user_data)

    # Login the user
    login_data = {
        "username": "test_user",
        "password": "test_password",
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

def test_refresh_token(db, client):
    # Create a new user through the API
    user_data = {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "test_password",
    }
    client.post("/api/auth/signup", json=user_data)

    # Login the user
    login_data = {
        "username": "test_user",
        "password": "test_password",
    }
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Extract refresh token from login response
    refresh_token = login_response.json()["refresh_token"]

    # Refresh the token
    refresh_response = client.get("/api/auth/refresh_token", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_response.status_code == 200
