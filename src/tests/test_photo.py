import pytest
from unittest.mock import AsyncMock, MagicMock
from src.database.db import Base
from src.tests.logger import logger
from src.repository.photo import create_photo
from src.database.models import Photo, User, Role

# def create_user(db: Session):
#     logger.critical(db)
#     try:
#         roles = ["Admin", "Moderator", "User"]
#         for role_name in roles:
#             existing_role = db.query(Role).filter(Role.role == role_name).first()
#             if not existing_role:
#                 db.add(Role(role=role_name))
#         db.commit()


# class TestTags(unittest.IsolatedAsyncioTestCase):
    

#     @classmethod
#     async def setUpClass(cls):
#         TEST_DATABASE_URL = "sqlite:///./test.db"
#         cls.engine = create_engine(TEST_DATABASE_URL)
#         SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
#         cls.db = SessionLocal()
#         cls.Base = Base
#         cls.Base.metadata.create_all(bind=cls.engine)
#         create_user(cls.db)
#         async with open(r"src\tests\test.jpg", "wb") as file:
#             r = await create_photo(user_id=3, file=file, description="test", tags=["string0", "string1", "string3", "string2", "string4"], db=cls.db)
#         logger.critical(r)

#     @classmethod
#     async def tearDownClass(cls):
#         # cls.db.close()
#         Base.metadata.drop_all(bind=cls.engine)
        
@pytest.mark.asyncio
async def test_create_photo():
    # Створюємо фейкові дані
    user_id = 1
    fake_file = AsyncMock()
    description = "Test description"
    tags = ["tag1", "tag2"]

    # Моделюємо поведінку бази даних та бібліотеки для завантаження файлів
    mock_db = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    mock_cloudinary = MagicMock()
    mock_cloudinary.uploader.upload.return_value = {
        "secure_url": "https://example.com/photo.jpg",
        "public_id": "abcd1234"
    }

    # Викликаємо функцію create_photo
    photo = await create_photo(user_id, fake_file, description, tags, mock_db)

    # Перевіряємо, чи було додано фото до бази даних
    assert mock_db.add.called
    assert mock_db.commit.called

    # Перевіряємо, чи було створено фото з правильним URL та описом
    assert photo.photo == "https://example.com/photo.jpg"
    assert photo.description == description

        

    # async def test_editing_tags(self):
    #     tags = ["string0, string1, string2, string3, string4"]
    #     result = await editing_tags(tags)
    #     assert result == ["string0", "string1", "string2", "string3", "string4"]

    #     tags = ["string0, string1, string3, string3, string2, string3, string4"]
    #     result = await editing_tags(tags)
    #     assert result == ["string0", "string1", "string3", "string2", "string4"]

    #     tags = ["string0", "string1", "string3", "string3", "string2", "string3", "string4"]
    #     result = await editing_tags(tags)
    #     assert result == ["string0"]

    #     tags = [""]
    #     result = await editing_tags(tags)
    #     assert result == []

    # async def test_create_tag(self):
    #     tags = ["string0", "string1", "string3", "string2", "string4"]
    #     result = await create_tag(self.photo.id, tags, self.session)
    #     logger.critical(result)




    # async def test_get_tags(self):
    #     result = await get_tags(self.photo.id, self.session)
    #     logger.critical(result)




