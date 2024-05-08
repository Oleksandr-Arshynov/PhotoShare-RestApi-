import pytest
from unittest.mock import MagicMock
from src.database.models import User, Role
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import src.database.db
from main import app
from src.database.models import Base
from src.database.db import get_db


# Тестова база даних
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
app.dependency_overrides[src.database.db.get_db] = lambda: TestingSessionLocal()


def create_static(session):
    try:
        roles = ["Admin", "Moderator", "User"]
        for role_name in roles:
            existing_role = session.query(Role).filter(Role.role == role_name).first()
            if not existing_role:
                session.add(Role(role=role_name))
        session.commit()
    except Exception:
        ...

    try:
        create_admin = User(
        username="Admin",
        email="Admin@gmail.com", 
        hashed_password="qwerty", 
        avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0cFYTSmgeLGCEAApBVBVkVcxe2COuA2sYja0IUfwe0w&s", 
        role_id=session.query(Role).filter(Role.role=="Admin").first().id
        )

        session.add(create_admin)
        session.commit()

        create_moderator = User(
            username="Moderator", 
            email="Moderator@gmail.com", 
            hashed_password="qwerty", 
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfhs8u11hfQyBqgGQSp_lWzoHkcSIjm6KGDC0gg567yg&s", 
            role_id=session.query(Role).filter(Role.role=="Moderator").first().id
        )

        session.add(create_moderator)
        session.commit()

        create_user = User(
            username="User", 
            email="User@gmail.com", 
            hashed_password="qwerty", 
            avatar="https://static6.depositphotos.com/1001599/647/i/450/depositphotos_6477379-stock-photo-fire-letters-a-z.jpg", 
            role_id=session.query(Role).filter(Role.role=="User").first().id
        )
        
        session.add(create_user)
        session.commit()
    except Exception:
        ...

@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    create_static(db)
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
def user_admin():
    admin = {
        "id": 1,
        "username": "Admin", 
        "email": "Admin@gmail.com", 
        "hashed_password": "qwerty", 
        "avatar": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0cFYTSmgeLGCEAApBVBVkVcxe2COuA2sYja0IUfwe0w&s", 
        "role_id": "Admin"
        }

    return admin


@pytest.fixture(scope="module")
def user_moderator():
    moderator = {
        "id": 2,
        "username": "Moderator", 
        "email": "Moderator@gmail.com", 
        "hashed_password": "qwerty", 
        "avatar": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfhs8u11hfQyBqgGQSp_lWzoHkcSIjm6KGDC0gg567yg&s", 
        "role_id": "Moderator"
        }
    

    return moderator


@pytest.fixture(scope="module")
def user_user():
    user = {
        "id": 3,
        "username": "User", 
        "email": "User@gmail.com", 
        "hashed_password": "qwerty", 
        "avatar": "https://static6.depositphotos.com/1001599/647/i/450/depositphotos_6477379-stock-photo-fire-letters-a-z.jpg", 
        "role_id": "User"
        }
    return user


@pytest.fixture()
def token_admin(client, user_admin, session):
    client.post("/api/auth/signup", json={
                                          "username": user_admin["username"],
                                          "password": user_admin["hashed_password"],
                                          "email": user_admin["email"]
                                          }
    )

    current_user: User = session.query(User).filter(User.email == user_admin["email"]).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user_admin["email"], "password": user_admin["hashed_password"]},
    )
    data = response.json()
    return data["access_token"]

# python -m pytest --cov .

