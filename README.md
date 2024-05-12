![обкладинка](logo.jpeg)

# Photo Share

**This project is an API for a photo gallery with the ability to add comments. Users can upload their photos, view photos from other users, and leave comments on them.**

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/Oleksandr-Arshynov/PhotoShare-RestApi-
    ```

2. Install dependencies:
    ```
    poetry install
    ```

3. Navigate to the directory:
    ```
    cd src
    ```

4. Run the container:
    ```
    docker-compose up
    ```

5. Apply changes:
    ```
    alembic upgrade head
    ```

6. Run the server:
    ```
    cd ..
    python main.py
    ```

***Usage***

### Authentication and Authorization

#### Register User [/auth/register]

Registers a new user with a role.

#### Admin Login [/auth/admin-login]

Authenticates an admin user and generates an access token.

#### Moderator Login [/auth/moderator-login]

Authenticates a moderator user and generates an access token.

#### User Login [/auth/user-login]

Authenticates a regular user and generates an access token.

#### Admin Router [/admin]

Provides endpoints accessible only to admin users.

#### Moderator Router [/moderator]

Provides endpoints accessible only to moderator users.

#### User Router [/user]

Provides endpoints accessible only to regular users.

### Admin Photo Management

#### Upload Photo [/admin/{upload_photo}]

Uploads a new photo.

#### Update Photo [/admin/{photo_id}]

Updates an existing photo.

#### Delete Photo [/admin/{photo_id}]

Deletes a photo.

#### Get All Photos [/admin]

Returns a list of all photos for the authenticated user.

#### Get Photo [/admin/{photo_id}]

Returns a specific photo based on its unique identifier.

#### Edit Photo Description [/admin/edit_photo_description/{user_id}/{photo_id}]

Updates the description of a photo based on its unique identifier.

#### Create Comment [/admin/create_comment]

Creates a new comment for a specific photo.

#### Update Comment [/admin/{comment_id}]

Updates an existing comment for a specific photo.

#### Delete Comment [/admin/{comment_id}]

Deletes a comment for a specific photo.

#### Delete User [/admin/delete-user/{user_id}]

Deletes a user based on their unique identifier.


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

### Delete Photo
- **Endpoint:** `/photo/{photo_id}`
- **Method:** DELETE
- **Description:** Deletes a photo.
- **Parameters:**
  - `photo_id`: ID of the photo to delete.
- **Response:** Returns the deleted photo details.

### Get All Photos
- **Endpoint:** `/photo/`
- **Method:** GET
- **Description:** Retrieves all photos for the current user.
- **Parameters:** None.
- **Response:** Returns a list of photo details for the current user.

### Get Photo by ID
- **Endpoint:** `/photo/{photo_id}`
- **Method:** GET
- **Description:** Retrieves a specific photo by its ID.
- **Parameters:**
  - `photo_id`: ID of the photo to retrieve.
- **Response:** Returns the details of the requested photo.

### Update Comment
- **Endpoint:** `/photo/{comment_id}`
- **Method:** PUT
- **Description:** Updates an existing comment for a photo.
- **Parameters:**
  - `comment_id`: ID of the comment to update.
  - `photo_id`: ID of the photo.
  - `user_id`: ID of the user.
  - `updated_comment`: The updated comment data.
- **Response:** Returns the updated comment details.


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
  - `schemas/`: Directory with schema
  - `tests/`: Directory containing tests
- `pyproject.toml`: Poetry configuration file containing project dependencies.
  

