
from src.repository.comment import (
    create_comment_rep,
    delete_comment_rep,
    update_comment_rep,
)
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
from src.auth.dependencies_auth import auth_service


router = APIRouter(prefix="/admin", tags=["admin"])

# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME,
    api_key=settings.CLD_API_KEY,
    api_secret=settings.CLD_API_SECRET,
)


@router.post("/{upload_photo}", status_code=status.HTTP_201_CREATED)
async def create_upload_photo(
    request: Request,
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Uploads a new photo.

    Args:
        request (Request): The incoming request.
        file (UploadFile): The image file to upload.
        description (str, optional): Description of the photo. Defaults to None.
        tags (List[str], optional): List of tags associated with the photo. Defaults to None.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The uploaded photo details.
    """
    user_id = 5  # Поки немає авторизації

    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.create_photo(user_id, file, description, tags, db)
    return photo


@router.put("/{photo_id}", status_code=status.HTTP_200_OK)
async def put_photo(
    request: Request,
    photo_id: int,
    file: UploadFile = File(None),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Updates an existing photo.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to update.
        file (UploadFile, optional): The new image file. Defaults to None.
        description (str, optional): The updated description of the photo. Defaults to None.
        tags (List[str], optional): The updated list of tags associated with the photo. Defaults to None.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The updated photo details.
    """

    user_id = 5  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.put_photo(
        user_id, photo_id, file, description, tags, db
    )
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    """
    Deletes a photo based on its unique identifier.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to delete.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The deleted photo details.
    """
    user_id = 5  # Поки немає авторизації
    photo = await repository_photo.delete_photo(user_id, photo_id, db)

    return photo


@router.get("", status_code=status.HTTP_200_OK)
async def get_photos(request: Request, db: Session = Depends(get_db)):
    """
    Returns a list of all photos for the authenticated user.

    Args:
        request (Request): The incoming request.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: List of photo details.
    """
    user_id = 5  # Поки немає авторизації
    photo = await repository_photo.get_photos(user_id, db)
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
async def get_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    """
    Returns a specific photo based on its unique identifier.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to retrieve.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The photo details.
    """
    user_id = 5  # Поки немає авторизації
    photo = await repository_photo.get_photo(user_id, photo_id, db)
    return photo


@router.put("/edit_photo_description/{user_id}/{photo_id}")
async def edit_photo_description(
    user_id: int, photo_id: int, new_description: str, db: Session = Depends(get_db)
):
    """
    Updates the description of a photo based on its unique identifier.

    Args:
        user_id (int): The ID of the user.
        photo_id (int): The ID of the photo to update.
        new_description (str): The new description for the photo.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The updated photo details.
    """
    # Перевіряємо, чи існує фотографія з вказаним ID
    photo = repository_photo.get_photo(user_id, photo_id, db)
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
    comment: CommentSchema, user_id: int, photo_id: int, db: Session = Depends(get_db)
):
    """
    Creates a new comment for a specific photo.

    Args:
        comment (CommentSchema): The comment data.
        user_id (int): The ID of the user.
        photo_id (int): The ID of the photo.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The created comment details.
    """

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    else:
        comment = create_comment_rep(db, user_id, photo_id, comment)
        return comment


@router.put("/{comment_id}")
async def update_comment(
    updated_comment: CommentUpdateSchema,
    comment_id: int,
    photo_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Updates an existing comment for a specific photo.

    Args:
        updated_comment (CommentUpdateSchema): The updated comment data.
        comment_id (int): The ID of the comment to update.
        photo_id (int): The ID of the photo.
        user_id (int): The ID of the user.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The updated comment details.
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
                Comment.user_id == user_id,
            )
            .first()
        )
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
            )

        comment = update_comment_rep(db, comment_id, updated_comment)
        return comment


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int, user_id: int, photo_id: int, db: Session = Depends(get_db)
):
    """
    Deletes a comment for a specific photo.

    Args:
        comment_id (int): The ID of the comment to delete.
        user_id (int): The ID of the user.
        photo_id (int): The ID of the photo.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The deleted comment details.
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
                Comment.user_id == user_id,
            )
            .first()
        )
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
            )

        comment = delete_comment_rep(db, photo_id, comment_id)
        return comment


# Ендпоінт видалення користувача за ID
@router.delete("/delete-user/{user_id}", dependencies=[Depends(auth_service.require_role())])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes a user based on their unique identifier.

    Args:
        user_id (int): The ID of the user to delete.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Confirmation message of the deleted user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    db.delete(user)
    db.commit()

    return {"msg": f"Користувач {user.username} видалений"}
