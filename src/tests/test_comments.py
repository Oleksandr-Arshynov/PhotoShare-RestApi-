from unittest.mock import MagicMock

import pytest


from src.database.models import Comment, User, Photo
from src.repository.comment import create_comment_rep, delete_comment_rep, update_comment_rep
from src.schemas.coment_schemas import CommentSchema, CommentUpdateSchema


@pytest.fixture
def user():
    return User(id=1, username='test_user', email="test@gmail.com", confirmed=True)


@pytest.fixture
def photo(user):
    return Photo(id=1, user_id=user.id, photo="test_photo")


@pytest.fixture
def session_mock():
    return MagicMock()


def test_create_comment(session_mock, user, photo):
    body = CommentSchema(comment="test comment")
    result = create_comment_rep(session_mock, user.id, photo.id, body)
    assert isinstance(result, Comment)
    assert result.comment == body.comment


def test_update_comment(session_mock):
    body = CommentUpdateSchema(id=1, comment="update comment")
    mocked_comment = MagicMock(scalar_one_or_none=MagicMock(return_value=Comment(id=1, comment="test comment")))
    session_mock.execute.return_value = mocked_comment
    result = update_comment_rep(session_mock, mocked_comment.id, body)
    assert result.comment == body.comment


def test_delete_comment(session_mock, photo):
    mocked_comment = MagicMock()
    mocked_comment.return_value = Comment(id=1, comment="test comment")
    result = delete_comment_rep(session_mock, photo.id, 1)
    session_mock.delete.assert_called_once()
