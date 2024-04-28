from typing import List
from fastapi import APIRouter, Depends, status, Request, FastAPI, File, UploadFile, Form
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import photo as repository_photo
from src.schemas.photo_schemas import PhotoCreate

from src.conf.config import settings
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix="/photo", tags=["photo"])


# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME, api_key=settings.CLD_API_KEY, api_secret=settings.CLD_API_SECRET
)


@router.post("/api/upload_photo/")
async def upload_photo(
    file: UploadFile = File(...),
    description: str = Form(...),
    user_id: int = Form(...),
    tags: List[str] = Form(...),
    db: Session = Depends(get_db)
):
    # Отримуємо завантажений файл та опис
    contents = await file.read()
    filename = file.filename

    # Генеруємо унікальний public_id
    public_id = f"{user_id}/{filename}"

    # Завантажуємо файл в Cloudinary
    response = cloudinary.uploader.upload(
        contents,
        folder=f"uploads/{user_id}",  # Папка, куди буде завантажено фото
        public_id=public_id,  # Ім'я файлу на Cloudinary
        description=description,
        tags=tags
    )

    # Отримуємо URL завантаженого фото з відповіді Cloudinary
    photo_url = response["secure_url"]
    
    # Зберігаємо фотографію в базі даних разом із public_id
    photo = await repository_photo.create_photo(
        user_id, photo_url, description, tags, public_id, db
    )
    return photo



@router.delete("/api/delete_photo/{user_id}/{photo_id}")
async def delete_photo(user_id: int, photo_id: int, db: Session = Depends(get_db)):
    photo = await repository_photo.get_photo(user_id, photo_id, db)
    if photo:
        # Видалення фотографії з Cloudinary
        cloudinary.uploader.destroy(photo.public_id, invalidate=True)
        # Видалення фотографії з бази даних
        await repository_photo.delete_photo(user_id, photo_id, db)
        return {"message": "Фотографія успішно видалена"}
    else:
        return {"message": "Фотографія не знайдена"}




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_photo(
    request: Request, body: PhotoCreate, db: Session = Depends(get_db)
):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.create_photo(
        user_id, body.photo, body.description, body.tags, db
    )
    return photo


@router.put("/{photo_id}", status_code=status.HTTP_200_OK)
async def put_photo(
    request: Request, photo_id: int, body: PhotoCreate, db: Session = Depends(get_db)
):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.put_photo(
        user_id, photo_id, body.photo, body.description, body.tags, db
    )
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.delete_photo(user_id, photo_id, db)
    return photo


@router.get("/", status_code=status.HTTP_200_OK)
async def get_photos(request: Request, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.get_photos(user_id, db)
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
async def get_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    photo = await repository_photo.get_photo(user_id, photo_id, db)
    return photo
