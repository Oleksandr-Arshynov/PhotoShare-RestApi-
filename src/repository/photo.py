from src.database.models import Tag, Photo, PhotoTagAssociation
from src.repository import tags as repository_tag
from sqlalchemy import and_
from datetime import datetime
from fastapi import HTTPException, status


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


#
async def create_photo(user_id: int, photo: str, description: str, tags: list, db: Session) -> Photo: # db: AsyncSession
    photo = Photo(photo=photo, description=description, user_id=user_id)

    if photo: # перевіряє що photo вдало створено
        db.add(photo)
        db.commit()
        tags = await repository_tag.create_tag(photo_id=photo.id, tags=tags, db=db) # додає теги
        photo = db.query(Photo).filter(Photo.id==photo.id).first()

        for num in range(0, len(tags)): # без цього не повертає теги 
            photo.tags[num].name

    return photo 


#
async def put_photo(user_id: int, photo_id: int, photo: str, description: str, tags: list, db: Session) -> Tag:
    post_photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()

    if post_photo: # перевіряє що photo знайдено вдало
        if photo: # перевіряє що photo не пусте 
            post_photo.photo = photo

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

        post_photo.updated_at = datetime.now() # дата редагування

    return post_photo


#
async def delete_photo(user_id: int, photo_id: int, db: Session) -> Photo | HTTPException:
    photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()

    if photo: # перевіряє що photo знайдено вдало
        tags = await repository_tag.get_tags(photo_id=photo.id, db=db)
        db.delete(photo) 
        db.commit()

        for num in range(0, len(tags)): # без цього не повертає теги, а просто {} або взягалі нічого
            photo.tags[num].name
        
        return photo # повертає видалений єлемент 
    
    else: # якщо photo не знайдено викликає помилку 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    

#
async def get_photo(user_id: int, photo_id: int, db: Session) -> Photo | HTTPException:
    photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()

    if photo: # перевіряє що photo знайдено вдало
        tags = await repository_tag.get_tags(photo_id=photo.id, db=db)
        for num in range(0, len(tags)): # без цього не повертає теги, а просто {} або взягалі нічого
            photo.tags[num].name
        
        return photo # повертає видалений єлемент 
    
    else: # якщо photo не знайдено викликає помилку 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    

async def get_photos(user_id: int, db: Session) -> Photo | HTTPException:
    photos = db.query(Photo).filter(Photo.user_id==user_id).all()

    if photos: # перевіряє що photo знайдено вдало
        for el in photos:
            tags = await repository_tag.get_tags(photo_id=el.id, db=db)
            for num in range(0, len(tags)): # без цього не повертає теги, а просто {} або взягалі нічого
                el.tags[num].name
    else: # якщо photo не знайдено викликає помилку 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photos