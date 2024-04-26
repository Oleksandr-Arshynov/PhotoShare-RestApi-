from src.database.models import Tag
from src.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from sqlalchemy.orm import Session









async def create_tag(tag: str, db: Session):
    admin_user = Tag(name=tag)
    db.add(admin_user)
    db.commit()
    return ''