from sqlmodel import SQLModel


class Message(SQLModel):
    """
    Generic message
    """

    message: str


class Token(SQLModel):
    """
    A JSON payload containing the access token.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """
    The contents of the JWT token.
    """

    sub: str | None = None
