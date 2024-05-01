from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.auth.dependencies_auth import (
    require_role,
)
from src.database.models import Photo, Comment


router = APIRouter(prefix="/moderator", tags=["moderator"])


# ----------МОДЕРАТОР----------


# Ендпоінт перегляду всіх коментарів
@router.get("/comments", dependencies=[Depends(require_role(2))])
def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments


# Ендпоінт видалення окремого коментаря для модератора
@router.delete("/delete-comment/{comment_id}", dependencies=[Depends(require_role(2))])
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Коментар не знайдено")

    db.delete(comment)
    db.commit()

    return {"msg": "Коментар видалено"}


# Ендпоінт перегляду всіх фото
@router.get("/photos", dependencies=[Depends(require_role(2))])
def get_all_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return photos


# Ендпоінт видалення окремого фото для модератора
@router.delete("/delete-photo/{photo_id}", dependencies=[Depends(require_role(2))])
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не знайдено")

    db.delete(photo)
    db.commit()

    return {"msg": "Фото видалено"}
