from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean, CheckConstraint

try:
    from src.database.db import Base
except:
    from database.db import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    avatar = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey('role.id'), default=3)
    number_of_photos = Column(Integer, default=0)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    role = relationship("Role", back_populates="user") 
    # ban = relationship("Ban", back_populates="user") 
    photo = relationship("Photo", back_populates="user")
    # comment = relationship("Сomment", back_populates="user") 


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False, unique=True)

    user = relationship("User", back_populates="role") 


# class Ban(Base):
#     __tablename__ = "bans"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     created_ban = Column('created_ban', DateTime, default=func.now(), nullable=True)
#     end_of_the_ban = Column('end_of_the_ban', DateTime, default=None, nullable=True)

#     user = relationship("User", back_populates="bans")


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True)


class Photo(Base):
    __tablename__ = "photo"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    photo = Column(String)
    public_id = Column(String)
    description = Column(String, nullable=True)
    public_id = Column(String)
    transformation_url_cartoon = Column(String)
    transformation_url_grayscale = Column(String)
    transformation_url_mask = Column(String)
    transformation_url_tilt = Column(String)

    user = relationship("User", back_populates="photo")  
    tags = relationship("Tag", secondary="photo_tag_association", backref="photo")


class PhotoTagAssociation(Base):
    __tablename__ = "photo_tag_association"
    photo_id = Column(Integer, ForeignKey("photo.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)


# class Comment(Base):
#     __tablename__ = "comments"
#     id = Column(Integer, primary_key=True)
#     photo_id = Column(Integer, ForeignKey('photos.id'), nullable=False)  
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
#     comment = Column(String(255), nullable=False)

#     photo = relationship("Photo", back_populates="comments") 
#     user = relationship("User", back_populates="comments")


# class LogoutUser(Base):
#     __tablename__ = "logout_users"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
#     access_token = Column(String)

#     user = relationship("User", back_populates="logout_users")


# class Rating(Base):
#     __tablename__ = "ratings"
#     id = Column(Integer, primary_key=True)
#     photo_id = Column(Integer, ForeignKey('photos.id'), nullable=False)  
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
#     rating = Column(Integer)
#     __table_args__ = (CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),)

    # user = relationship("User", back_populates="rating")
    # photo = relationship("Photo", back_populates="rating")