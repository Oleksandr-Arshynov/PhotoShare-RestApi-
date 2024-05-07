from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)

from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import user as repository_user


router = APIRouter(prefix="/user", tags=["user"])

USER_ID = 1

@router.get("")
async def get_me_info( 
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = USER_ID # Поки немає авторизації
    user = await repository_user.get_user(user_id, db)
    if user == None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/{username}")
async def get_user_info( 
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    user = await repository_user.get_username(username, db)
    if user == None:
        raise HTTPException(status_code=404, detail="Username not found")
    return user

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_photo(
    request: Request,
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Creates a new photo.

    Args:
        request (Request): The incoming request.
        file (UploadFile): The image file to upload.
        description (str, optional): The description of the photo. Defaults to None.
        tags (List[str], optional): The list of tags associated with the photo. Defaults to None.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The created photo details.
    """

    user_id = USER_ID  # Поки немає авторизації

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

    user_id = USER_ID  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.put_photo(
        user_id, photo_id, file, description, tags, db
    )
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    """
    Deletes a photo.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to delete.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The deleted photo details.
    """
    user_id = USER_ID  # Поки немає авторизації
    photo = await repository_photo.delete_photo(user_id, photo_id, db)

    return photo


@router.get("", status_code=status.HTTP_200_OK)
async def get_photos(request: Request, db: Session = Depends(get_db)):
    """
    Retrieves all photos for the current user.

    Args:
        request (Request): The incoming request.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: A list of photo details for the current user.
    """

    user_id = USER_ID  # Поки немає авторизації
    photo = await repository_photo.get_photos(user_id, db)
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
async def get_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific photo by its ID.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to retrieve.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The details of the requested photo.
    """

    user_id = USER_ID  # Поки немає авторизації
    photo = await repository_photo.get_photo(user_id, photo_id, db)
    return photo


@router.put("/edit_photo_description/{user_id}/{photo_id}")
async def edit_photo_description(
    user_id: int, photo_id: int, new_description: str, db: Session = Depends(get_db)
):
    """
    Edits the description of a photo.

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
    Creates a new comment for a photo.

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
    Updates an existing comment for a photo.

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
