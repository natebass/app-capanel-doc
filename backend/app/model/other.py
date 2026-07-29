from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel
from sqlmodel.main import SQLModelConfig


class Message(SQLModel):
    """
    A message for an API response.
    """

    message: str
    success: bool = True
    status: str | None = None
    code: str | int | None = None
    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class Token(SQLModel):
    """
    A JSON payload containing the access token. The names follow the JWT spec (RFC 7519).
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """
    The contents of the JWT token with a subject claim. The names follow the JWT spec (RFC 7519).
    """

    sub: str | None = None
