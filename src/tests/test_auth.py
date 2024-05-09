import pytest
from src.database.db import SessionLocal
from src.auth.dependencies_auth import auth_service
from src.database.models import User
from src.schemas import schemas_auth


@pytest.fixture(scope="module")
def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
        
        
def test_create_user(client):
    # Create a new user
    body = schemas_auth.UserCreate(
        username="test_user",
        email="test_user@example.com",
        password="test_password",  # Assuming password is passed here
    )
    response = client.post("api/auth/signup", json=dict(body))  # Convert UserCreate object to dictionary
    assert response.status_code == 201



  # імпортуємо модель User з відповідного місця у вашому проекті

def test_login_user(client):
    # Assuming you have a valid user in your database with the following credentials
    username = "test_user@example.com"
    password = "test_password"

    # Send a POST request to the login endpoint with the username and password
    response = client.post("api/auth/login", data={"username": username, "password": password})

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200


