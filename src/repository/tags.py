from src.database.models import Tag, PhotoTagAssociation
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session


#
async def create_tag(photo_id: int, tags: list, db: Session) -> list: # db: AsyncSession
    
    if tags != []: # перевірка на пустий список
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

#
async def get_tags(photo_id: int, db: Session):
    tags = db.query(Tag).join(PhotoTagAssociation, Tag.id == PhotoTagAssociation.tag_id).filter(PhotoTagAssociation.photo_id == photo_id).all()
    return tags


#
async def editing_tags(tags: list) -> list:
    tags = tags[0].split(",") # Розділяємо теги
    if len(tags[0]) != 0: # Перевірка на наявність тегів
        unique_list = []
        for item in tags: # видаляємо дублі без втрати порядку
            if item not in unique_list:
                unique_list.append(item)

        if len(unique_list) >= 5:
            count_tag = 5
        elif len(unique_list) < 5:
            count_tag = len(unique_list)

        new_list = []
        for num in range(0, count_tag): # Повертаємо лише перші 5 тегів
            new_list.append(unique_list[num])
        return new_list
    return []