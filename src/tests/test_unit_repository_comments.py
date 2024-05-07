from datetime import date
import unittest
from unittest.mock import MagicMock, AsyncMock, Mock
import sys


from sqlalchemy.orm import Session

from src.schemas.coment_schemas import CommentSchema,CommentUpdateSchema
from src.database.models import Comment, User, Photo
from src.repository.comment import create_comment_rep, delete_comment_rep, update_comment_rep


class TestCommentRepository(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self) -> None:
        self.user = User(id=1, username='test_user',email = "test@gmail.com", confirmed=True)
        self.photo = Photo(id=1, user_id=self.user.id, photo="test_photo")
        self.session = MagicMock(spec=Session)
    
    def test_create_contact(self):
        body = CommentSchema(comment="test comment")
        result = create_comment_rep(self.session, self.user.id, self.photo.id, body)
        self.assertIsInstance(result, Comment)
        self.assertEqual(result.comment, body.comment)
        


    def test_update_contact(self):
        body = CommentUpdateSchema(id=1, comment="update comment")
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Comment(id=1, comment="test comment")
        self.session.execute.return_value = mocked_contact
        result = update_comment_rep(self.session, mocked_contact.id ,body)
        self.assertEqual(result.comment, body.comment)



    def test_delete_contact(self):
        mocked_comment = MagicMock()
        mocked_comment.return_value = Comment(id=1, comment="test comment")

        result = delete_comment_rep(self.session, self.photo.id, 1)
        self.session.delete.assert_called_once()