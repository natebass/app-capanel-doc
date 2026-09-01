import warnings
from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import (
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_origins(value: str) -> list[str]:
    """Split a comma-separated list of URLs into its entries.

    The value is kept as a plain string rather than a list field because
    ``pydantic-settings`` JSON-decodes a list-typed setting before any
    validator runs, which rejects the comma-separated form a deployment
    actually sets.

    Args:
        value: A comma-separated string, possibly empty.

    Returns:
        The individual entries, stripped of surrounding whitespace.
    """
    return [item.strip() for item in value.split(",") if item.strip()]


def _to_origin(url: str) -> str | None:
    """Reduce a URL to the browser origin the ``Origin`` header will carry.

    A browser sends only the scheme, host, and port, so any path has to be
    dropped: ``https://opensacorg.github.io/app-capanel-web`` is a valid
    :data:`Settings.FRONTEND_HOST` for building links into a GitHub Pages
    project site, but the matching origin is ``https://opensacorg.github.io``.

    Args:
        url: A full URL, or a bare origin.

    Returns:
        The ``scheme://host[:port]`` origin, or ``None`` when *url* has no
        scheme and host to take one from.
    """
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        return None
    return f"{parts.scheme}://{parts.netloc}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # Public base URL of the front end, used to build links in emails.  It may
    # include a path when the site is served from a sub-path, such as a GitHub
    # Pages project site.
    FRONTEND_HOST: str = "http://localhost:5173"
    # Extra browser origins allowed to call the API, beyond FRONTEND_HOST.  Set
    # this when the same deployment is reachable under more than one origin,
    # for example a Pages sub-domain and a custom domain.
    BACKEND_CORS_ORIGINS: str = ""
    FASTAPI_ENV: Literal["development"] | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """List every browser origin permitted to call the API.

        The front end and the API are deployed separately, so calls from the
        browser are cross-origin and each allowed origin has to be named.
        :data:`FRONTEND_HOST` is always included, reduced to its origin, and
        :data:`BACKEND_CORS_ORIGINS` adds any others.

        Returns:
            The distinct origins, in the order they were configured.
        """
        origins: list[str] = []
        for url in (self.FRONTEND_HOST, *_split_origins(self.BACKEND_CORS_ORIGINS)):
            origin = _to_origin(url)
            if origin is not None and origin not in origins:
                origins.append(origin)
        return origins

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    DATABASE_URL: PostgresDsn
    RESEARCH_FILE_SOURCE_URI: str
    # Where the California School Dashboard indicator files are read from.
    # Defaults to the state's own web server, so no local copy is needed.
    DASHBOARD_FILE_SOURCE_URI: str = (
        "https://www3.cde.ca.gov/researchfiles/cadashboard/"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _use_psycopg_driver(cls, value: str | PostgresDsn) -> str:
        database_url = str(value)
        for scheme in ("postgres://", "postgresql://"):
            if database_url.startswith(scheme):
                return database_url.replace(scheme, "postgresql+psycopg://", 1)
        return database_url

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
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.FASTAPI_ENV == "development":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        for host in self.DATABASE_URL.hosts():
            self._check_default_secret("DATABASE_URL password", host["password"])
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()
