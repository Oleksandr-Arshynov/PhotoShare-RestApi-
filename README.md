# Photo Share

This project is an API for a photo gallery with the ability to add comments. Users can upload their photos, view photos from other users, and leave comments on them.

## Installation

1. Clone the repository:
    git clone https://github.com/Oleksandr-Arshynov/PhotoShare-RestApi-

2. Встановити залежності:
    poetry install

3. Зайти в директорію:
    cd src

4. Зробити міграцію:
    alembic revision --autogenerate -m 'Init'

5. Застосувати зміни:
    alembic upgrade head

6. Запустити контейнер:
    docker-compose up

7. Запустити сервер:
    python main.py


## Usage

### Upload Photo
- **Endpoint:** `/photo/`
- **Method:** POST
- **Description:** Uploads a new photo.
- **Parameters:**
  - `file`: The photo file to upload (required).
  - `description`: Description of the photo (optional).
  - `tags`: List of tags for the photo (optional).
- **Response:** Returns the uploaded photo details.

### Edit Photo Description
- **Endpoint:** `/photo/edit_photo_description/{user_id}/{photo_id}`
- **Method:** PUT
- **Description:** Edits the description of an existing photo.
- **Parameters:**
  - `user_id`: User ID of the photo owner.
  - `photo_id`: ID of the photo to edit.
  - `new_description`: New description for the photo.
- **Response:** Returns the updated photo details.

### Transformations

#### Cartoonify Photo
- **Endpoint:** `/photo/cartoon/{photo_id}`
- **Method:** POST
- **Description:** Applies a cartoon effect to the photo.
- **Parameters:**
  - `photo_id`: ID of the photo to transform.
- **Response:** Returns URLs for the transformed and original photos.

#### Grayscale Photo
- **Endpoint:** `/photo/grayscale/{photo_id}`
- **Method:** POST
- **Description:** Converts the photo to grayscale.
- **Parameters:**
  - `photo_id`: ID of the photo to transform.
- **Response:** Returns URLs for the transformed and original photos.

#### Mask Photo
- **Endpoint:** `/photo/face/{photo_id}`
- **Method:** POST
- **Description:** Applies a mask effect to the photo.
- **Parameters:**
  - `photo_id`: ID of the photo to transform.
- **Response:** Returns URLs for the transformed and original photos.

#### Tilt Photo
- **Endpoint:** `/photo/tilt/{photo_id}`
- **Method:** POST
- **Description:** Tilts the photo with an outline effect.
- **Parameters:**
  - `photo_id`: ID of the photo to transform.
- **Response:** Returns URLs for the transformed and original photos.

## Project Structure

- `main.py`: Main application file containing FastAPI routes.
- `src/`: Directory containing application logic.
  - `database/`: Directory with database configurations and models.
  - `repository/`: Directory with repository classes for interacting with the database.
  - `conf/`: Directory containing application configurations.
  - `routes/`: Directory containing FastAPI router modules.
- `pyproject.toml`: Poetry configuration file containing project dependencies.
