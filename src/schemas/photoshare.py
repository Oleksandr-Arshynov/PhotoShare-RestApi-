from pydantic import BaseModel
from typing import List, Optional


class RoleBase(BaseModel):
    role: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True




class UserBase(BaseModel):
    username: str
    email: str
    password: str
    avatar: Optional[str] = None
    confirmed: bool = False
    role_id: int = 3
    number_of_photos: int = 0
    refresh_token: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    role: Role

    class Config:
        orm_mode = True


class PhotoBase(BaseModel):
    photo: str
    description: Optional[str] = None
    tags:  Optional[List]


class PhotoCreate(PhotoBase):
    pass


class Photo(PhotoBase):
    id: int
    user: User
    
    class Config:
        orm_mode = True







class BanBase(BaseModel):
    user_id: int


class BanCreate(BanBase):
    pass


class Ban(BanBase):
    id: int
    created_ban: Optional[str] = None
    end_of_the_ban: Optional[str] = None
    user: User

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True






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
        orm_mode = True


class LogoutUserBase(BaseModel):
    user_id: int
    access_token: str


class LogoutUserCreate(LogoutUserBase):
    pass


class LogoutUser(LogoutUserBase):
    id: int
    user: User

    class Config:
        orm_mode = True


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
