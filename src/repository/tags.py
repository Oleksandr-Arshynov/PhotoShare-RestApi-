from src.database.models import Tag, PhotoTagAssociation
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session



async def create_tag(photo_id: int, tags: list[str], db: Session) -> Tag: # db: AsyncSession
    if tags != None:
        for tag in tags:
            result = db.query(Tag).filter(Tag.name==tag).first()
            if result:
                photo_tag = PhotoTagAssociation(photo_id=photo_id, tag_id=result.id)
                db.add(photo_tag)
                db.commit()
            else:
                new_tag = Tag(name=tag)
                db.add(new_tag)
                db.commit()
                result = db.query(Tag).filter(Tag.name==tag).first()
                photo_tag = PhotoTagAssociation(photo_id=photo_id, tag_id=result.id)
                db.add(photo_tag)
                db.commit()
    return tags