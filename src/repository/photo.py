from src.database.models import Tag, Photo, PhotoTagAssociation
from src.repository import tags as repository_tag
from sqlalchemy import and_
from src.schemas.photoshare import TagCreate
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session



async def create_photo(user_id: int, photo: str, description: str, tags: list[str] | None, db: Session) -> Photo: # db: AsyncSession
    photo = Photo(photo=photo, description=description, user_id=user_id)
    db.add(photo)
    db.commit()
    tags = await repository_tag.create_tag(photo_id=photo.id, tags=tags, db=db)

    return photo

async def put_photo(user_id: int, photo_id: int, photo: str, description: str, tags: list, db: Session) -> Tag:
    pass

#
async def delete_photo(user_id: int, photo_id: int, db: Session):
    photo = db.query(Photo).filter(and_(Photo.user_id==user_id, Photo.id==photo_id)).first()
    if photo:
        db.delete(photo)
        db.commit()
        return photo
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")