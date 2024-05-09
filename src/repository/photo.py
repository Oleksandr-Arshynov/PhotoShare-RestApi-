import os
import uuid
import qrcode
import shutil
import cloudinary.uploader
from sqlalchemy import and_
from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from src.conf.config import settings
from src.repository import tags as repository_tag
from src.database.models import Tag, Photo, PhotoTagAssociation, User, Comment
from src.tests.logger import logger



# Встановлюємо конфігурацію Cloudinary
cloudinary.config(
    cloud_name=settings.CLD_NAME, api_key=settings.CLD_API_KEY, api_secret=settings.CLD_API_SECRET
)



async def create_photo(user_id: int, file: UploadFile, description: str, tags: list, db: Session) -> Photo: # db: AsyncSession
    # Отримуємо завантажений файл та опис
    contents = await file.read()
    # Завантажуємо файл в Cloudinary
    response = cloudinary.uploader.upload(
        contents,
        folder=f"uploads/{user_id}",  # Папка, куди буде завантажено фото
        public_id=str(uuid.uuid4()),  # Ім'я файлу на Cloudinary
        context = f"alt={description}",
        tags=tags
        )
    # Отримуємо URL завантаженого фото з відповіді Cloudinary
    
    photo_url = response["secure_url"]
    public_id = response["public_id"]
    
    photo = Photo(photo=photo_url, description=description, user_id=user_id, public_id=public_id)
    logger.critical(photo)
    if photo: # перевіряє що photo вдало створено
        db.add(photo)
        db.commit()
        tags = await repository_tag.create_tag(photo_id=photo.id, tags=tags, db=db) # додає теги
        photo = db.query(Photo).filter(Photo.id==photo.id).first()
        user = db.query(User).filter(User.id==photo.user_id).first()
        user.number_of_photos += 1
        db.commit()
        for num in range(0, len(tags)): # без цього не повертає теги 
            photo.tags[num].name

        return db.query(Photo).filter(Photo.id==photo.id).first()
    else:
        cloudinary.uploader.destroy(photo.public_id)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Photo no created"
        )


async def put_photo(user_id: int, photo_id: int, file: UploadFile, description: str, tags: list, db: Session) -> Tag:
    post_photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()

    if post_photo: # перевіряє що photo знайдено вдало
        if description: # перевіряє що description не пусте 
            post_photo.description = description

        if tags: # перевіряє що tags не пусте
            
            photo_tag = db.query(PhotoTagAssociation).filter(PhotoTagAssociation.photo_id==photo_id).all()
            for el in photo_tag: # видаляє старі теги
                db.delete(el)
            db.commit()

            tags = await repository_tag.create_tag(photo_id=photo_id, tags=tags, db=db) # додає тові теги

            for num in range(0, len(tags)): # без цього не повертає теги, а просто {} або взягалі нічого
                post_photo.tags[num].name

        if file != None:
            contents = await file.read()
            # Видаляємо файл в Cloudinary
            cloudinary.uploader.destroy(post_photo.public_id)
            # Завантажуємо файл в Cloudinary
            response = cloudinary.uploader.upload(
                contents,
                folder=f"uploads/{user_id}",  # Папка, куди буде завантажено фото
                public_id=str(uuid.uuid4()),  # Ім'я файлу на Cloudinary
                context = f"alt={description}",
                tags=tags
            )
            # Отримуємо URL завантаженого фото з відповіді Cloudinary
            post_photo.photo = response["secure_url"]
            post_photo.public_id = response["public_id"]
            db.commit()
            try:
                shutil.rmtree(f"src/static/users/{user_id}/{photo_id}") # видалення qr
            except:
                ...

        post_photo.updated_at = datetime.now() # дата редагування

    return db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()



async def delete_photo(user_id: int, photo_id: int, db: Session) -> Photo | HTTPException:
    photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()

    if photo: # перевіряє що photo знайдено вдало
        cloudinary.uploader.destroy(photo.public_id)
        try:
            shutil.rmtree(f"src/static/users/{user_id}/{photo_id}") # видалення qr
        except:
            ...

        comments = db.query(Comment).filter(Comment.photo_id==photo.id).all() # Видалення коментарів
        for comment in comments:
            db.delete(comment) 
        db.commit()

        tags = await repository_tag.get_tags(photo_id=photo.id, db=db)
        db.delete(photo) 
        db.commit()

        user = db.query(User).filter(User.id==photo.user_id).first()
        user.number_of_photos -= 1
        db.commit()

        for num in range(0, len(tags)): # без цього не повертає теги, а просто {} або взягалі нічого
            photo.tags[num].name
        
        return photo # повертає видалений єлемент 
    
    else: # якщо photo не знайдено викликає помилку 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")



async def get_photo(user_id: int, photo_id: int, db: Session) -> Photo | HTTPException:
    photo = (
        db.query(Photo)
        .filter(and_(Photo.user_id == user_id, Photo.id == photo_id))
        .first()
    )

    if photo:  # перевіряє що photo знайдено вдало
        tags = await repository_tag.get_tags(photo_id=photo.id, db=db)
        for num in range(
            0, len(tags)
        ):  # без цього не повертає теги, а просто {} або взягалі нічого
            photo.tags[num].name

        return photo  # повертає видалений єлемент

    else:  # якщо photo не знайдено викликає помилку 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )


async def get_photos(user_id: int, db: Session) -> Photo | HTTPException:
    photos = db.query(Photo).filter(Photo.user_id == user_id).all()

    if photos:  # перевіряє що photo знайдено вдало
        for el in photos:
            tags = await repository_tag.get_tags(photo_id=el.id, db=db)
            for num in range(
                0, len(tags)
            ):  # без цього не повертає теги, а просто {} або взягалі нічого
                el.tags[num].name
    else:  # якщо photo не знайдено викликає помилку 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photos


# new
async def create_qr_code(url: str, user_id: int, photo_id: int) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="blue", back_color="white") 
    
    # Перевірка, чи існує шлях до директорії
    if not os.path.exists(f"src/static/users/{user_id}/{photo_id}"):
        os.makedirs(f"src/static/users/{user_id}/{photo_id}")
    filename = f"{str(uuid.uuid4())}.png" 

    # Збереження QR-коду з вставленим зображенням
    qr_img.save(f"src/static/users/{user_id}/{photo_id}/" + filename)
    return filename


# new
async def delete_qr_code(filename: str, user_id: int, photo_id: int):
    file_path = f"src/static/users/{user_id}/{photo_id}/" + filename 
    try:
        os.remove(file_path)
        print(f"Файл {file_path} успішно видалено.")
        return True
    except FileNotFoundError:
        print(f"Файл {file_path} не знайдено.")
        return False
    except Exception as e:
        print(f"Виникла помилка при видаленні файлу: {e}")
        return False





def update_photo_description(photo_id: int, new_description: str, db: Session):
    # Знайти фотографію за її ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        # Оновити опис фотографії
        photo.description = new_description
        # Зберегти зміни в базі даних
        db.commit()
        # Повернути оновлену фотографію
        return photo
    else:
        # Якщо фотографія не знайдена, повернути None
        return None
    
def rollback_photo_description(photo_id: int, db: Session):
    # Знайти фотографію за її ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        # Повернути початковий опис фотографії
        photo.description = ""
        # Зберегти зміни в базі даних
        db.commit()
        # Повернути оновлену фотографію
        return photo
    else:
        # Якщо фотографія не знайдена, повернути None
        return None
    
from cloudinary import api

# Оновити метадані фотографії в Cloudinary
def update_cloudinary_metadata(public_id, new_description):
    try:
        # Викликати метод update для оновлення метаданих
        result = api.update(public_id, context = f"alt={new_description}")
        
        # Перевірити статус відповіді на успішність
        if result['result'] != 'ok':
            # Обробити помилку, якщо не вдалося оновити метадані
            raise Exception("Не вдалося оновити метадані фотографії в Cloudinary")
    except Exception as e:
        # Обробити будь-які винятки та повернути False у випадку невдалого оновлення
        print(f"Помилка при оновленні метаданих фотографії в Cloudinary: {e}")
        return False
    return True


