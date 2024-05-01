from datetime import datetime
from pydantic import Field
from pydantic import BaseModel
from typing import List, Optional

from src.schemas.photo_schemas import Photo
from src.schemas.user_schemas import User


class CommentSchema(BaseModel):
    comment: str = Field(min_length=1, max_length=255)


class CommentUpdateSchema(CommentSchema):
    pass



class CommentResponse(BaseModel):
    id: int
    user_id: int
    photo_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CommentBase(BaseModel):
    photo_id: int
    user_id: int
    comment: str
    
class CommentUpdate(CommentBase):
    id: int
    photo: Photo
    user: User

    class Config:
        from_attributes = True
