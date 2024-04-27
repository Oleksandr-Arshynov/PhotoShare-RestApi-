from src.database.models import Tag, PhotoTagAssociation, Photo
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session



async def create_tag(photo_id: int, tags: list, db: Session) -> list: # db: AsyncSession
    
    if tags != []: # перевірка на пустий список
        tags = set(tags) # видалення дублікатів
        
        for tag in tags:
            result = db.query(Tag).filter(Tag.name==tag).first() # перевірка на існування тегу

            if result: # якщо тег існує додає до таблиці PhotoTagAssociation
                photo_tag = PhotoTagAssociation(photo_id=photo_id, tag_id=result.id)
                db.add(photo_tag)
                db.commit()

            else: # якщо тег не існує додає тег до бази а потім до таблиці PhotoTagAssociation
                new_tag = Tag(name=tag)
                db.add(new_tag)
                db.commit()

                result = db.query(Tag).filter(Tag.name==tag).first()
                photo_tag = PhotoTagAssociation(photo_id=photo_id, tag_id=result.id)
                db.add(photo_tag)
                db.commit()

    return tags # повертає додані теги


async def get_tags(photo_id: int, db: Session):
    tags = db.query(Tag).join(PhotoTagAssociation, Tag.id == PhotoTagAssociation.tag_id).filter(PhotoTagAssociation.photo_id == photo_id).all()
    return tags