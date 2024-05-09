import cloudinary.uploader
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, status

from src.database.db import get_db
from src.database.models import User
from src.repository import photo as repository_photo
from src.conf.config import settings
from src.auth.dependencies_auth import auth_service


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
        dict: Dictionary containing transformed image URL, original image URL, and filename of QR code.
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

    filename = await repository_photo.create_qr_code(
        url=photo.transformation_url_cartoon, user_id=current_user.id, photo_id=photo_id
    )
    if filename != "":
        if photo.qr_url_cartoon:
            result = await repository_photo.delete_qr_code(
                filename=photo.qr_url_cartoon, user_id=current_user.id, photo_id=photo_id
            )
            if result:
                photo.qr_url_cartoon = filename
                photo.updated_at = datetime.now()  # дата редагування
                db.commit()

    # Повернути URL трансформованого зображення та оригінального зображення
    return {
        "transformed_image_url": transformed_image["secure_url"],
        "original_image_url": original_image["secure_url"],
        "filename": photo.qr_url_cartoon,
    }


# OK
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
        dict: Dictionary containing transformed image URL, original image URL, and filename of QR code.
    """
    user_id = current_user.id # Тимчасово, доки немає автентифікації
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

    filename = await repository_photo.create_qr_code(
        url=photo.transformation_url_grayscale, user_id=user_id, photo_id=photo_id
    )
    if filename != "":
        if photo.qr_url_grayscale:
            result = await repository_photo.delete_qr_code(
                filename=photo.qr_url_grayscale, user_id=user_id, photo_id=photo_id
            )
            if result:
                photo.qr_url_grayscale = filename
                photo.updated_at = datetime.now()  # дата редагування
                db.commit()

    # Повернути URL трансформованого зображення та оригінального зображення
    return {
        "transformed_image_url": transformed_image["secure_url"],
        "original_image_url": original_image["secure_url"],
        "filename": photo.qr_url_grayscale,
    }


# OK
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
        dict: Dictionary containing transformed image URL, original image URL, and filename of QR code.
    """
    user_id = current_user.id  # Тимчасово, доки немає автентифікації
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

    filename = await repository_photo.create_qr_code(
        url=photo.transformation_url_mask, user_id=user_id, photo_id=photo_id
    )
    if filename != "":
        if photo.qr_url_mask:
            result = await repository_photo.delete_qr_code(
                filename=photo.qr_url_mask, user_id=user_id, photo_id=photo_id
            )
            if result:
                photo.qr_url_mask = filename
                photo.updated_at = datetime.now()  # дата редагування
                db.commit()

    # Повернути URL трансформованого зображення та оригінального зображення
    return {
        "transformed_image_url": transformed_image["secure_url"],
        "original_image_url": original_image["secure_url"],
        "filename": photo.qr_url_mask,
    }


# OK
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
        dict: Dictionary containing transformed image URL, original image URL, and filename of QR code.
    """
    user_id = current_user.id  # Тимчасово, доки немає автентифікації
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

    filename = await repository_photo.create_qr_code(
        url=photo.transformation_url_tilt, user_id=user_id, photo_id=photo_id
    )
    if filename != "":
        if photo.qr_url_tilt:
            result = await repository_photo.delete_qr_code(
                filename=photo.qr_url_tilt, user_id=user_id, photo_id=photo_id
            )
            if result:
                photo.qr_url_tilt = filename
                photo.updated_at = datetime.now()  # дата редагування
                db.commit()

    # Повернути URL трансформованого зображення та оригінального зображення
    return {
        "transformed_image_url": transformed_image["secure_url"],
        "original_image_url": original_image["secure_url"],
        "filename": photo.qr_url_tilt,
    }
