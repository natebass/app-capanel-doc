import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import get_datetime_utc

if TYPE_CHECKING:
    from app.model.item import Item


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    force_password_reset: bool | None = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)
    # User preferences
    last_viewed_cds: str | None = Field(default=None, max_length=14)
    force_password_reset: bool = Field(default=False)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    force_password_reset: bool = False


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserPreferencesUpdate(SQLModel):
    """Request model for updating user preferences."""

    last_viewed_cds: str | None = Field(default=None, max_length=14)


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ForcePasswordResetRequest(SQLModel):
    emails: list[EmailStr] = Field(default_factory=list)
    include_all_active_users: bool = False
