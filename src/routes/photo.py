from pathlib import Path
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    FastAPI,
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
from cloudinary import CloudinaryImage


import qrcode
from io import BytesIO

router = APIRouter(prefix="/photo", tags=["photo"])


# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME,
    api_key=settings.CLD_API_KEY,
    api_secret=settings.CLD_API_SECRET,
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_upload_photo(
    request: Request,
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db),
):
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

    user_id = 5  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.put_photo(
        user_id, photo_id, file, description, tags, db
    )
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 5  # Поки немає авторизації
    photo = await repository_photo.delete_photo(user_id, photo_id, db)

    return photo


@router.get("", status_code=status.HTTP_200_OK)
async def get_photos(request: Request, db: Session = Depends(get_db)):
    user_id = 5  # Поки немає авторизації
    photo = await repository_photo.get_photos(user_id, db)
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
async def get_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 5  # Поки немає авторизації
    photo = await repository_photo.get_photo(user_id, photo_id, db)
    return photo


@router.put("/edit_photo_description/{user_id}/{photo_id}")
async def edit_photo_description(
    user_id: int, photo_id: int, new_description: str, db: Session = Depends(get_db)
):
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
