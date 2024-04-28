from typing import List
from fastapi import APIRouter, Depends, status, Request, File, UploadFile, Form
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import photo as repository_photo
from src.repository import tags as repository_tags



router = APIRouter(prefix="/photo", tags=["photo"])




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_upload_photo(
    request: Request,
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db)
):
    user_id = 1  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.create_photo(user_id, file, description, tags, db)
    return photo



@router.put("/{photo_id}", status_code=status.HTTP_200_OK)
async def put_photo(
    request: Request,
    photo_id: int,
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db)):

    user_id = 1  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.put_photo(user_id, photo_id, file, description, tags, db)
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
