import os
import secrets
import warnings
from typing import Annotated, Any, Literal
from urllib.parse import quote_plus

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """
    Use the top level .env file (one level above ./backend/).
    Access not expires in 60 minutes * 24 hours * 8 days = 8 days
    """

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = "California Accountability Panel"
    SENTRY_DSN: HttpUrl | None = None
    DB_CONNECTION_MODE: Literal["auto", "local", "cloudsql"] = "auto"
    DATABASE_URL: str | None = None
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    CLOUD_SQL_INSTANCE_CONNECTION_NAME: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not configured")
        return self.DATABASE_URL

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """
        Complain at startup if a secret is "changethis",
        """
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    @model_validator(mode="after")
    def _enforce_cloud_run_environment(self) -> Self:
        if os.getenv("K_SERVICE") and self.ENVIRONMENT != "production":
            raise ValueError(
                'ENVIRONMENT must be "production" when running on Cloud Run.'
            )
        return self

    @model_validator(mode="after")
    def _populate_database_url(self) -> Self:
        if self.DATABASE_URL:
            return self

        if not (self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB):
            raise ValueError(
                "DATABASE_URL is required, or set POSTGRES_USER/POSTGRES_PASSWORD/"
                "POSTGRES_DB and either POSTGRES_SERVER (local/tcp) or "
                "CLOUD_SQL_INSTANCE_CONNECTION_NAME (Cloud SQL socket)."
            )

        encoded_password = quote_plus(self.POSTGRES_PASSWORD)

        def _build_local_postgres_url() -> str:
            if not self.POSTGRES_SERVER:
                raise ValueError(
                    "DB_CONNECTION_MODE=local requires POSTGRES_SERVER to be set."
                )
            return (
                "postgresql+psycopg://"
                f"{self.POSTGRES_USER}:{encoded_password}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        def _build_cloudsql_url() -> str:
            if not self.CLOUD_SQL_INSTANCE_CONNECTION_NAME:
                raise ValueError(
                    "DB_CONNECTION_MODE=cloudsql requires "
                    "CLOUD_SQL_INSTANCE_CONNECTION_NAME to be set."
                )
            return (
                "postgresql+psycopg://"
                f"{self.POSTGRES_USER}:{encoded_password}"
                f"@/{self.POSTGRES_DB}"
                f"?host=/cloudsql/{self.CLOUD_SQL_INSTANCE_CONNECTION_NAME}"
            )

        if self.DB_CONNECTION_MODE == "local":
            self.DATABASE_URL = _build_local_postgres_url()
            return self

        if self.DB_CONNECTION_MODE == "cloudsql":
            self.DATABASE_URL = _build_cloudsql_url()
            return self

        # Auto mode:
        # - production prefers Cloud SQL when configured
        # - local/staging prefer direct Postgres TCP when configured
        # - fallback to whichever option is available
        if self.ENVIRONMENT == "production" and self.CLOUD_SQL_INSTANCE_CONNECTION_NAME:
            self.DATABASE_URL = _build_cloudsql_url()
            return self

        if self.POSTGRES_SERVER:
            self.DATABASE_URL = _build_local_postgres_url()
            return self

        if self.CLOUD_SQL_INSTANCE_CONNECTION_NAME:
            self.DATABASE_URL = _build_cloudsql_url()
            return self

        raise ValueError(
            "Could not resolve database connection in DB_CONNECTION_MODE=auto. "
            "Set POSTGRES_SERVER for local/tcp or set "
            "CLOUD_SQL_INSTANCE_CONNECTION_NAME for Cloud SQL."
        )


settings = Settings()
