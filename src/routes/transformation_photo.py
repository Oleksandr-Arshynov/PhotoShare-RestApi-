import cloudinary.uploader
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, status

from src.database.db import get_db
from src.database.models import User
from src.repository import photo as repository_photo
from src.conf.config import settings
from src.auth.dependencies_auth import auth_service

import qrcode
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter(prefix="/transformation_photo", tags=["transformation_photo"])


# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME,
    api_key=settings.CLD_API_KEY,
    api_secret=settings.CLD_API_SECRET,
)


# OK
@router.post("/cartoon/{photo_id}", status_code=status.HTTP_200_OK)
async def cartoon_transformation_photo(
    request: Request, photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Apply cartoon transformation to a photo.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to transform.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        StreamingResponse: Response containing transformed image, original image, and QR code.
    """

    photo = await repository_photo.get_photo(current_user.id, photo_id, db)

    # Зберегти оригінальне зображення в Cloudinary
    original_image = cloudinary.uploader.upload(photo.photo)

    # Виконати трансформації за допомогою Cloudinary
    transformed_image = cloudinary.uploader.upload(
        photo.photo,
        transformation=[{"effect": "cartoonify", "radius": "max"}],
        format="jpg",
    )

    # Оновити URL трансформованого зображення та оригінального зображення у базі даних
    photo.transformation_url_cartoon = transformed_image["secure_url"]
    photo.photo = original_image["secure_url"]
    db.add(photo)
    db.commit()

    # Створення QR-коду
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(photo.transformation_url_cartoon)
    qr.make(fit=True)

    # Генерація QR-коду у форматі PNG
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image_bytes = BytesIO()
    qr_image.save(qr_image_bytes, "PNG")
    qr_image_bytes.seek(0)

    # Повернення відповіді з зображенням QR-коду та URL зображень
    return StreamingResponse(
        content=qr_image_bytes,
        media_type="image/png",
        headers={
            'X-Transformed-Image-URL': transformed_image["secure_url"],
            'X-Original-Image-URL': original_image["secure_url"]
        }
    )





from fastapi.responses import StreamingResponse

@router.post("/grayscale/{photo_id}", status_code=status.HTTP_200_OK)
async def transformation_photo_grayscale(
    request: Request, photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Apply grayscale transformation to a photo.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to transform.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        StreamingResponse: Response containing transformed image, original image, and QR code.
    """
    user_id = current_user.id
    photo = await repository_photo.get_photo(user_id, photo_id, db)

    # Зберегти оригінальне зображення в Cloudinary
    original_image = cloudinary.uploader.upload(photo.photo)

    # Виконати трансформації за допомогою Cloudinary
    transformed_image = cloudinary.uploader.upload(
        photo.photo, transformation=[{"effect": "grayscale"}], format="jpg"
    )

    # Оновити URL трансформованого зображення та оригінального зображення у базі даних
    photo.transformation_url_grayscale = transformed_image["secure_url"]
    photo.photo = original_image["secure_url"]
    db.add(photo)
    db.commit()

    # Створення QR-коду
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(photo.transformation_url_grayscale)
    qr.make(fit=True)

    # Генерація QR-коду у форматі PNG
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image_bytes = BytesIO()
    qr_image.save(qr_image_bytes, "PNG")
    qr_image_bytes.seek(0)

    # Повернення відповіді з зображенням QR-коду та URL зображень
    return StreamingResponse(
        content=qr_image_bytes,
        media_type="image/png",
        headers={
            'X-Transformed-Image-URL': transformed_image["secure_url"],
            'X-Original-Image-URL': original_image["secure_url"]
        }
    )


@router.post("/face/{photo_id}", status_code=status.HTTP_200_OK)
async def transformation_photo_face(
    request: Request, photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Apply face transformation to a photo.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to transform.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        StreamingResponse: Response containing transformed image, original image, and QR code.
    """
    user_id = current_user.id
    photo = await repository_photo.get_photo(user_id, photo_id, db)

    # Зберегти оригінальне зображення в Cloudinary
    original_image = cloudinary.uploader.upload(photo.photo)

    # Виконати трансформації за допомогою Cloudinary
    transformed_image = cloudinary.uploader.upload(
        photo.photo,
        transformation=[
            {"gravity": "face", "height": 200, "width": 200, "crop": "thumb"},
            {"radius": "max"},
            {"fetch_format": "auto"},
        ],
    )

    # Оновити URL трансформованого зображення та оригінального зображення у базі даних
    photo.transformation_url_mask = transformed_image["secure_url"]
    photo.photo = original_image["secure_url"]
    db.add(photo)
    db.commit()

    # Створення QR-коду
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(photo.transformation_url_mask)
    qr.make(fit=True)

    # Генерація QR-коду у форматі PNG
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image_bytes = BytesIO()
    qr_image.save(qr_image_bytes, "PNG")
    qr_image_bytes.seek(0)

    # Повернення відповіді з зображенням QR-коду та URL зображень
    return StreamingResponse(
        content=qr_image_bytes,
        media_type="image/png",
        headers={
            'X-Transformed-Image-URL': transformed_image["secure_url"],
            'X-Original-Image-URL': original_image["secure_url"]
        }
    )


@router.post("/tilt/{photo_id}", status_code=status.HTTP_200_OK)
async def transformation_photo_tilt(
    request: Request, photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Apply tilt transformation to a photo.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to transform.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        StreamingResponse: Response containing transformed image, original image, and QR code.
    """
    user_id = current_user.id
    photo = await repository_photo.get_photo(user_id, photo_id, db)

    # Зберегти оригінальне зображення в Cloudinary
    original_image = cloudinary.uploader.upload(photo.photo)

    # Виконати трансформації за допомогою Cloudinary
    transformed_image = cloudinary.uploader.upload(
        photo.photo,
        transformation=[
            {"height": 400, "width": 250, "crop": "fill"},
            {"angle": 20},
            {"effect": "outline", "color": "brown"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Оновити URL трансформованого зображення та оригінального зображення у базі даних
    photo.transformation_url_tilt = transformed_image["secure_url"]
    photo.photo = original_image["secure_url"]
    db.add(photo)
    db.commit()

    # Створення QR-коду
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(photo.transformation_url_tilt)
    qr.make(fit=True)

    # Генерація QR-коду у форматі PNG
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image_bytes = BytesIO()
    qr_image.save(qr_image_bytes, "PNG")
    qr_image_bytes.seek(0)

    # Повернення відповіді з зображенням QR-коду та URL зображень
    return StreamingResponse(
        content=qr_image_bytes,
        media_type="image/png",
        headers={
            'X-Transformed-Image-URL': transformed_image["secure_url"],
            'X-Original-Image-URL': original_image["secure_url"]
        }
    )
