from pydantic import BaseModel
from typing import Optional

from schemas.user_schemas import User


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
