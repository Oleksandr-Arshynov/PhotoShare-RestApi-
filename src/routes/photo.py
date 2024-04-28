from typing import List
from fastapi import APIRouter, Depends, status, Request, FastAPI, File, UploadFile, Form
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import photo as repository_photo
from src.repository import tags as repository_tags
from src.schemas.photo_schemas import PhotoCreate
from src.schemas.tag_schemas import TagCreate

from src.conf.config import settings
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix="/photo", tags=["photo"])


# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME, api_key=settings.CLD_API_KEY, api_secret=settings.CLD_API_SECRET
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_upload_photo(
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db)
):
    user_id = 1  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)

    # Отримуємо завантажений файл та опис
    contents = await file.read()
    filename = file.filename

    # Завантажуємо файл в Cloudinary
    response = cloudinary.uploader.upload(
        contents,
        folder=f"uploads/{user_id}",  # Папка, куди буде завантажено фото
        public_id=filename,  # Ім'я файлу на Cloudinary
        description=description,
        tags=tags
    )

    # Отримуємо URL завантаженого фото з відповіді Cloudinary
    photo_url = response["secure_url"]
    
    photo = await repository_photo.create_photo(user_id, photo_url, description, tags, db)
    return photo



@router.put("/{photo_id}", status_code=status.HTTP_200_OK)
async def put_photo(request: Request, photo_id: int, body: PhotoCreate, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.put_photo(user_id, photo_id, body.photo, body.description, body.tags, db)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.delete_photo(user_id, photo_id, db)
    return photo


@router.get("", status_code=status.HTTP_200_OK)
async def get_photos(request: Request, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.get_photos(user_id, db)
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
async def get_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.get_photo(user_id, photo_id, db)
    return photo
