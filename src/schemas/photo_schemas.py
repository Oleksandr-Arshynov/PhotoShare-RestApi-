from pydantic import BaseModel
from typing import List, Optional

from src.schemas.tag_schemas import Tag, TagBase
from src.schemas.user_schemas import User


class PhotoBase(BaseModel):
    user_id: int
    photo: str
    description: Optional[str] = None


class PhotoCreate(PhotoBase):
    tags: Optional[List[TagBase]] = []


class Photo(PhotoBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    user: User
    tags: List[Tag]

    class Config:
        orm_mode = True
