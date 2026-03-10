import os

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.model.user import User, UserCreate
from app.service import crud

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    """
    Creates one superuser.
    """
    if settings.ENVIRONMENT == "production" and (
        "FIRST_SUPERUSER" not in os.environ
        or "FIRST_SUPERUSER_PASSWORD" not in os.environ
    ):
        return

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
