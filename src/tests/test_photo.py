from src.tests.logger import logger  
from src.database.models import User, Photo, Role, Tag

filename = "photo.jpg"
new_filename = "new_photo.jpg"

def test_create_photo(client, session):
    with open(filename, "rb") as file:
        response = client.post(
            "/api/photo",
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


def test_create_photo_no_data(client, session):
    with open(filename, "rb") as file:
        response = client.post(
            "/api/photo",
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


def test_create_photo_no_file(client):
    response = client.post(
        "/api/photo",
        files={"file": None},
        data={"description": "", "tags": [""]}
    )
        
    assert response.status_code == 400, "Bad Request"
    data = response.json()
    assert data["detail"] == "There was an error parsing the body"


def test_put_photo(client, session):
    public_id = session.query(Photo).filter(Photo.id==2).first().public_id
    with open(new_filename, "rb") as file:
        response = client.put(
            f"/api/photo/{2}",
            files={"file": file},
            data={"description": "test", "tags": ["1,2,3,4,5"]}
        )
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["id"] == 2
    assert data["user_id"] == 1
    assert data["description"] == "test"
    assert data["public_id"] != public_id


def test_put_photo_no_file(client, session):
    photo = session.query(Photo).filter(Photo.id==2).first()
    tags = [tag.name for tag in photo.tags] 
    public_id = photo.public_id
    response = client.put(
        f"/api/photo/{2}",
        files={"file": ""},
        data={"description": "new", "tags": ["6,7,8,9,10"]}
    )

    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["id"] == 2
    assert data["user_id"] == 1
    assert data["description"] == "new"
    assert data["public_id"] == public_id
    assert [tag["name"] for tag in data["tags"]] != tags


def test_delete_photo(client, session):
    response = client.delete(f"/api/photo/{1}")
    assert response.status_code == 200, "OK"
    data = response.json()
    photo = session.query(Photo).filter(Photo.id==data["id"]).first()
    assert photo == None

    response = client.delete(f"/api/photo/{2}")
    assert response.status_code == 200, "OK"
    data = response.json()
    photo = session.query(Photo).filter(Photo.id==data["id"]).first()
    assert photo == None


