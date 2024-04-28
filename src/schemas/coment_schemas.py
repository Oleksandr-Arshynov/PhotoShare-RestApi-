from pydantic import BaseModel

from schemas.photo_schemas import Photo
from schemas.user_schemas import User


class CommentBase(BaseModel):
    photo_id: int
    user_id: int
    comment: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    photo: Photo
    user: User

    class Config:
        from_attributes = True
