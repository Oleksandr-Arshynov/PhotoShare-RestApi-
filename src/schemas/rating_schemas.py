from pydantic import BaseModel

from schemas.photo_schemas import Photo
from schemas.user_schemas import User


class RatingBase(BaseModel):
    photo_id: int
    user_id: int
    rating: int


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    user: User
    photo: Photo

    class Config:
        orm_mode = True
