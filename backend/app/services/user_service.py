from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.models.user import User
from app.repositories.user_repository import create_user, get_user


def register_user(db: Session, name: str) -> User:
    return create_user(db, name=name)


def get_user_or_404(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
