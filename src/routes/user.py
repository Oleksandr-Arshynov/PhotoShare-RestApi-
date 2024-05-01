from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from src.auth.dependencies_auth import get_current_user

from src.database.db import get_db

from src.database.models import User, Photo, Comment
from src.schemas.coment_schemas import CommentUpdate
from src.schemas.photo_schemas import PhotoUpdate


router = APIRouter(prefix="/user", tags=["user"])

# ----------ЮЗЕР----------


# Ендпоінт перегляду всіх коментарів інших користувачів
@router.get("/comments")
def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments


# Ендпоінт перегляду всіх фото інших користувачів
@router.get("/photos")
def get_all_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return photos


# Видалення власного фото
@router.delete("/delete-photo/{photo_id}")
def delete_own_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Шукаємо фото за ID та перевіряємо, чи є власником поточний користувач
    photo = (
        db.query(Photo)
        .filter(Photo.id == photo_id, Photo.owner_id == current_user.id)
        .first()
    )
    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Фото не знайдено або ви не маєте дозволу видалити це фото",
        )

    db.delete(photo)
    db.commit()

    return {"msg": "Фото успішно видалено"}


# Видалення власного коментаря
@router.delete("/delete-comment/{comment_id}")
def delete_own_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Перевіряємо, чи існує коментар і чи належить він поточному користувачу
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.owner_id == current_user.id)
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Коментар не знайдено або ви не маєте дозволу видалити цей коментар",
        )

    db.delete(comment)
    db.commit()

    return {"msg": "Коментар успішно видалено"}


# Редагування власного коментаря
@router.put("/update-comment/{comment_id}")
def update_own_comment(
    comment_id: int,
    comment_update: CommentUpdate,  # Коментар, що містить новий текст
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.owner_id == current_user.id)
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Коментар не знайдено або ви не маєте права його редагувати",
        )

    comment.text = comment_update.text
    db.commit()

    return {"msg": "Коментар успішно оновлено"}


# Редагування власного фото
@router.put("/update-photo/{photo_id}")
def update_own_photo(
    photo_id: int,
    photo_update: PhotoUpdate,  # Об'єкт із новим описом або іншими метаданими
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = (
        db.query(Photo)
        .filter(Photo.id == photo_id, Photo.owner_id == current_user.id)
        .first()
    )
    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Фото не знайдено або ви не маєте права його редагувати",
        )

    if photo_update.description:
        photo.description = photo_update.description

    db.commit()

    return {"msg": "Фото успішно оновлено"}
