from src.tests.logger import logger  
from src.database.models import User, Photo, Role, Tag

def test_create_photo(client, session):
    with open("test.jpg", "rb") as file:
        response = client.post(
            "/api/user",
            files={"file": ("test.jpg", file, "image/jpeg")},
            data={"description": "Test Photo", "tags": ["tag1, tag2"]}
        )

    assert response.status_code == 201, "Created"
    data = response.json()
    photo = session.query(Photo).filter(Photo.id==data["id"]).first()
    assert data["id"] == photo.id
    assert data["user_id"] == photo.user_id
    assert data["description"] == photo.description
    assert data["photo"] == photo.photo
    assert data["public_id"] == photo.public_id
    assert data["tags"][0]["name"] == photo.tags[0].name
    assert data["tags"][1]["name"] == photo.tags[1].name


def test_create_photo1(client, session):
    with open("test.jpg", "rb") as file:
        response = client.post(
            "/api/user",
            files={"file": ("test.jpg", file, "image/jpeg")},
            data={"description": "", "tags": [""]}
        )

    assert response.status_code == 201, "Created"
    data = response.json()
    photo = session.query(Photo).filter(Photo.id==data["id"]).first()
    assert data["id"] == photo.id
    assert data["user_id"] == photo.user_id
    assert data["description"] == photo.description
    assert data["photo"] == photo.photo
    assert data["public_id"] == photo.public_id