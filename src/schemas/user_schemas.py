from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    role: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True


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
        from_attributes = True


class LogoutUserBase(BaseModel):
    user_id: int
    access_token: str


class LogoutUserCreate(LogoutUserBase):
    pass


class LogoutUser(LogoutUserBase):
    id: int
    user: User

    class Config:
        from_attributes = True
