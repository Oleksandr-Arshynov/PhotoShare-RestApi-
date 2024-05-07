import pytest
from main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import src.database.db
from src.database.models import Base
from src.database.db import get_db

# Створення тестової бази даних
TEST_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
app.dependency_overrides[src.database.db.get_db] = lambda: TestingSessionLocal()

client = TestClient(app)

#@pytest.fixture(autouse=True)
#def setup_and_teardown():
    # Створення таблиць перед тестами
    #src.database.models.Base.metadata.create_all(bind=engine)
    #yield
    # Видалення таблиць після тестів
    #src.database.models.Base.metadata.drop_all(bind=engine)

# Реєстрація користувача
def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "new_user",
            "password": "securepassword",
            "email": "newuser@example.com",
        },
    )
    assert response.status_code == 200
    assert "msg" in response.json() and response.json()["msg"] == "Користувач зареєстрований"

# Повторна реєстрація того ж користувача
def test_register_duplicate_user():
    client.post(
        "/auth/register",
        json={
            "username": "duplicate_user",
            "password": "securepassword",
            "email": "duplicate@example.com",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "duplicate_user",
            "password": "securepassword",
            "email": "duplicate2@example.com",
        },
    )
    assert response.status_code == 400
    assert "Користувач вже існує" in response.json()["detail"]

# Авторизація з правильними обліковими даними
def test_login_user():
    client.post(
        "/auth/register",
        json={
            "username": "user_login",
            "password": "securepassword",
            "email": "loginuser@example.com",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "user_login",
            "password": "securepassword",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json() and response.json()["token_type"] == "bearer"

# Авторизація з неправильним паролем
def test_login_with_incorrect_password():
    client.post(
        "/auth/register",
        json={
            "username": "incorrect_password",
            "password": "securepassword",
            "email": "incorrectpass@example.com",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "incorrect_password",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Невірне ім'я користувача або пароль" in response.json()["detail"]