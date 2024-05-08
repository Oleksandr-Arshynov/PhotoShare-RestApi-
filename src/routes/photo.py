from src.auth.dependencies_auth import auth_service
from src.repository.comment import create_comment_rep, update_comment_rep
from src.database.models import Photo, Comment, User
from src.schemas.coment_schemas import (
    CommentResponse,
    CommentSchema,
    CommentUpdateSchema,
)
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    File,
    UploadFile,
    Form,
)
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import photo as repository_photo
from src.repository import tags as repository_tags

from src.conf.config import settings
import cloudinary.uploader
from src.conf import messages
from src.schemas.user_schemas import UserCreate
from src.tests.logger import logger


router = APIRouter(prefix="/photo", tags=["photo"])

# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME,
    api_key=settings.CLD_API_KEY,
    api_secret=settings.CLD_API_SECRET,
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_photo(
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    CREATE PHOTO

    Method: POST
    URL: /photo

    Description:
    This endpoint allows a user to upload a new photo.

    Parameters:
    - file (UploadFile, required): The image file that the user wants to upload.
    - description (str, optional): Description of the photo that the user can add.
    - tags (List[str], optional): List of tags associated with the photo.

    Response:
    Returns the created photo object.

    Status Codes:
    - 201: Photo created successfully.
    """
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.create_photo(
        current_user.id, file, description, tags, db
    )
    return photo


@router.put("/{photo_id}", status_code=status.HTTP_200_OK)
async def put_photo(
    request: Request,
    photo_id: int,
    file: UploadFile = File(None),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    UPDATE PHOTO

    Method: PUT
    URL: /photo/{photo_id}

    Description:
    This endpoint allows a user to update an existing photo.

    Parameters:
    - photo_id (int, path, required): The ID of the photo to be updated.
    - file (UploadFile, optional): The new image file to replace the existing one.
    - description (str, optional): New description for the photo.
    - tags (List[str], optional): New list of tags for the photo.

    Response:
    Returns the updated photo object.

    Status Codes:
    - 200: Photo updated successfully.
    """

    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.put_photo(
        current_user.id, photo_id, file, description, tags, db
    )
    logger.critical(photo.photo)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    DELETE PHOTO

    Method: DELETE
    URL: /photo/{photo_id}

    Description:
    This endpoint allows a user to delete an existing photo.

    Parameters:
    - photo_id (int, path, required): The ID of the photo to be deleted.

    Response:
    Returns the deleted photo object.

    Status Codes:
    - 200: Photo deleted successfully.
    """
    photo = await repository_photo.delete_photo(current_user.id, photo_id, db)

    return photo


@router.get("", status_code=status.HTTP_200_OK)
async def get_photos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    GET PHOTOS

    Method: GET
    URL: /photo

    Description:
    This endpoint allows a user to retrieve all photos associated with their account.

    Response:
    Returns a list of photo objects.

    Status Codes:
    - 200: Photos retrieved successfully.
    """
    photo = await repository_photo.get_photos(current_user.id, db)
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
async def get_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    GET PHOTO

    Method: GET
    URL: /photo/{photo_id}

    Description:
    This endpoint allows a user to retrieve a specific photo by its ID.

    Parameters:
    - photo_id (int, path, required): The ID of the photo to be retrieved.

    Response:
    Returns the requested photo object.

    Status Codes:
    - 200: Photo retrieved successfully.
    """
    photo = await repository_photo.get_photo(current_user.id, photo_id, db)
    return photo


@router.put("/edit_photo_description/{user_id}/{photo_id}")
async def edit_photo_description(
    user_id: int,
    photo_id: int,
    new_description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    EDIT PHOTO DESCRIPTION

    Method: PUT
    URL: /photo/edit_photo_description/{user_id}/{photo_id}

    Description:
    This endpoint allows a user to edit the description of a photo.

    Parameters:
    - user_id (int, path, required): The ID of the user who owns the photo.
    - photo_id (int, path, required): The ID of the photo whose description is to be edited.
    - new_description (str, body, required): The new description for the photo.

    Response:
    Returns the updated photo object with the new description.

    Status Codes:
    - 200: Photo description updated successfully.
    """
    # Перевіряємо, чи існує фотографія з вказаним ID
    photo = repository_photo.get_photo(current_user.id, photo_id, db)
    if photo is None:
        raise HTTPException(status_code=404, detail="Фотографія не знайдена")

    # Оновлюємо опис фотографії в базі даних
    photo = repository_photo.update_photo_description(photo_id, new_description, db)

    # Оновлюємо опис фотографії в Cloudinary
    try:
        repository_photo.update_cloudinary_metadata(photo.public_id, new_description)
    except Exception as e:
        # Відкатити зміни в базі даних, якщо виникла помилка в Cloudinary
        repository_photo.rollback_photo_description(photo_id, db)
        raise HTTPException(
            status_code=500,
            detail=f"Помилка під час оновлення опису фотографії в Cloudinary: {str(e)}",
        )

    return photo


@router.post("/create_comment", response_model=CommentResponse)
async def create_comment(
    comment: CommentSchema,
    user_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    CREATE COMMENT

    Method: POST
    URL: /photo/create_comment

    Description:
    This endpoint allows a user to create a comment on a photo.

    Parameters:
    - comment (CommentSchema, body, required): The comment object containing the user's comment details.
    - user_id (int, body, required): The ID of the user creating the comment.
    - photo_id (int, body, required): The ID of the photo on which the comment is being created.

    Response:
    Returns the created comment object.

    Status Codes:
    - 200: Comment created successfully.
    """

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    else:
        comment = create_comment_rep(db, current_user.id, photo_id, comment)
        return comment


@router.put("/{comment_id}")
async def update_comment(
    updated_comment: CommentUpdateSchema,
    comment_id: int,
    photo_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    UPDATE COMMENT

    Method: PUT
    URL: /photo/{comment_id}

    Description:
    This endpoint allows a user to update their comment on a photo.

    Parameters:
    - updated_comment (CommentUpdateSchema, body, required): The updated comment object.
    - comment_id (int, path, required): The ID of the comment to be updated.
    - photo_id (int, body, required): The ID of the photo on which the comment is being updated.
    - user_id (int, body, required): The ID of the user who owns the comment.

    Response:
    Returns the updated comment object.

    Status Codes:
    - 200: Comment updated successfully.
    """

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    else:
        comment = (
            db.query(Comment)
            .filter(
                Comment.id == comment_id,
                Comment.photo_id == photo_id,
                Comment.user_id == current_user.id,
            )
            .first()
        )
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
            )

        comment = update_comment_rep(db, comment_id, updated_comment)
        return comment
