import uuid
from datetime import datetime
from typing import Annotated, Any, cast

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import get_datetime_utc
from app.model.user import User

sa_datetime_type = cast(Any, DateTime(timezone=True))

Timestamp = Annotated[
    datetime | None,
    Field(default_factory=get_datetime_utc, sa_type=sa_datetime_type),
]


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)


class Item(ItemBase, table=True):
    """
    An item that is owned by a user.
    """

    __tablename__ = "items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Timestamp = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )
    owner: User = Relationship(back_populates="items")


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: Timestamp = Field(default_factory=get_datetime_utc)


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
