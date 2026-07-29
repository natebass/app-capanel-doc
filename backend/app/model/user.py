import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, cast

from pydantic.alias_generators import to_camel
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.main import EmailStr, SQLModelConfig

from app.core.utils import get_datetime_utc

if TYPE_CHECKING:
    from app.model.item import Item

sa_datetime_type = cast(Any, DateTime(timezone=True))

Timestamp = Annotated[
    datetime | None,
    Field(default_factory=get_datetime_utc, sa_type=sa_datetime_type),
]


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    force_password_reset: bool | None = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    last_viewed_cds: str | None = Field(default=None, max_length=14)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: Timestamp = Field(default_factory=get_datetime_utc)
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)
    last_viewed_cds: str | None = Field(default=None, max_length=14)
    force_password_reset: bool = Field(default=False)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: Timestamp = Field(default_factory=get_datetime_utc)
    force_password_reset: bool = Field(default=False)


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserPreferencesUpdate(SQLModel):
    last_viewed_cds: str | None = Field(default=None, max_length=14)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class ForcePasswordResetRequest(SQLModel):
    emails: list[EmailStr] = Field(default_factory=list)
    include_all_active_users: bool = False

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)
