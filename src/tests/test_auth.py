import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database.db import get_db, Base
from main import app
from src.database.models import Base

# Тестова база даних
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Зміна залежності на тестову
app.dependency_overrides[get_db] = lambda: TestingSessionLocal()

def test_admin_role_on_first_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "firstuser",
            "password": "firstpassword",
            "email": "first@example.com",
        },
    )
    assert response.status_code == 200
    user = response.json()["user"]
    assert user["role"] == "admin"

def test_register_user_and_check_role():
    # Зареєструємо першого користувача, який є адміністратором
    client.post(
        "/auth/register",
        json={
            "username": "firstuser",
            "password": "firstpassword",
            "email": "first@example.com",
        },
    )

    # Зареєструємо іншого користувача, який має бути юзером
    response = client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "password": "secondpassword",
            "email": "second@example.com",
        },
    )
    assert response.status_code == 200
    user = response.json()["user"]
    assert user["role"] == "user"

def test_login_and_check_role():
    # Реєструємо користувача
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com",
        },
    )

    # Авторизуємося та отримуємо токен
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Перевіряємо ендпоінт, який доступний лише адміністратору
    response = client.get(
        "/auth/admin-endpoint",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Очікуємо помилку, оскільки користувач не адміністратор

    # Перевірка ендпоінту для модератора
    response = client.get(
        "/auth/moderator-endpoint",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Очікуємо помилку, оскільки користувач не модератор
