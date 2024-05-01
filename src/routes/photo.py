from typing import List
from fastapi import APIRouter, Depends, status, Request, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.db import get_db
from src.database.models import Photo
from src.repository import photo as repository_photo
from src.repository import tags as repository_tags
import qrcode 
import cloudinary.uploader
from starlette.responses import FileResponse
from fastapi.responses import RedirectResponse


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
    response = RedirectResponse(url="http://localhost:8000/", status_code=302)
    return response


@router.put("/{photo_id}", status_code=status.HTTP_200_OK)
async def put_photo(
    request: Request,
    photo_id: int,
    file: UploadFile = File(None),
    description: str = Form(None),
    tags: List[str] = Form(None),
    db: Session = Depends(get_db)):
    user_id = 1  # Поки немає авторизації
    tags = await repository_tags.editing_tags(tags)
    photo = await repository_photo.put_photo(user_id, photo_id, file, description, tags, db)
    


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    print(photo_id)
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




# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name="dclrmc6yi", api_key="913556912999135", api_secret="2ZzHdqBkl17s9KN1tkoM0qT0Rwk"
)

@router.get("/qr_code/{photo_id}", status_code=status.HTTP_200_OK)
async def create_qr(request: Request, photo_id: int, db: Session = Depends(get_db)):
    user_id = 1
    photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()
    if photo:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(photo.photo)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="blue", back_color="white")
        
        # Збереження QR-коду з вставленим зображенням
        qr_img.save("src/service/qr_code.png")
        return FileResponse("src/service/qr_code.png", media_type='image') 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

