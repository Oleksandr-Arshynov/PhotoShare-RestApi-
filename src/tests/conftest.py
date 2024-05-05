import pytest
from unittest.mock import MagicMock 
from src.database.models import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def admin_user():
    return {
        "username": "Admin", 
        "email": "Admin@gmail.com", 
        "password": "qwerty", 
        "avatar": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0cFYTSmgeLGCEAApBVBVkVcxe2COuA2sYja0IUfwe0w&s", 
        "lore": "Admin"
        }


@pytest.fixture(scope="module")
def moderator_user():
    return {
        "username": "Moderator", 
        "email": "Moderator@gmail.com", 
        "password": "qwerty", 
        "avatar": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfhs8u11hfQyBqgGQSp_lWzoHkcSIjm6KGDC0gg567yg&s", 
        "lore": "Moderator"
        }


@pytest.fixture(scope="module")
def user_user():
    return {
        "username": "User", 
        "email": "User@gmail.com", 
        "password": "qwerty", 
        "avatar": "https://static6.depositphotos.com/1001599/647/i/450/depositphotos_6477379-stock-photo-fire-letters-a-z.jpg", 
        "lore": "User"
        }


# python -m pytest --cov .

