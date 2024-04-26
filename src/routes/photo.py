from datetime import date
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from sqlalchemy.orm import Session
from src.database.db import get_db

from src.database.models import User
from src.repository import photo as repository_photo
from src.schemas.photoshare import PhotoCreate, Photo



router = APIRouter(prefix='/photo', tags=['photo'])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_photo(request: Request, body: PhotoCreate, db: Session = Depends(get_db)):
    user_id=1
    photo = await repository_photo.create_photo(user_id, body.photo, body.description, body.tags, db)
    return photo


@router.put("/", status_code=status.HTTP_200_OK)
async def put_photo(request: Request, body: PhotoCreate, db: Session = Depends(get_db)):
    user_id=1
    photo = await repository_photo.put_photo(user_id, body.photo, body.description, body.tags, db)
    return photo


#
@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id=1
    photo = await repository_photo.delete_photo(user_id, photo_id, db)
    return photo