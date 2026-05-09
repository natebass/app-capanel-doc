"""General-purpose utilities for the application.

Provides helpers for environment-variable parsing, email rendering and
delivery, JWT token generation/verification, and datetime helpers.
"""

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import emails
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


def env_bool(name: str, default: bool) -> bool:
    """Read an environment variable and interpret it as a boolean.

    Truthy values are ``"1"``, ``"true"``, ``"yes"``, ``"y"``, and ``"on"``
    (case-insensitive).  Anything else is considered falsy.

    Args:
        name: Name of the environment variable.
        default: Value to return when the variable is not set.

    Returns:
        The parsed boolean, or *default* when the variable is absent.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_csv_set(raw: str) -> set[str] | None:
    """Parse a comma-separated string into a set of stripped, non-empty values.

    Args:
        raw: The raw comma-separated string (e.g. ``"2024, 2025"``).

    Returns:
        A ``set[str]`` of the parsed values, or ``None`` if the result
        would be empty.
    """
    values = {v.strip() for v in raw.split(",") if v.strip()}
    return values or None


# ---------------------------------------------------------------------------
# Email helpers
# ---------------------------------------------------------------------------


@dataclass
class EmailData:
    """Container for a rendered email ready to be sent.

    Attributes:
        html_content: The rendered HTML body of the email.
        subject: The subject line of the email.
    """

    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """Render a Jinja2 email template to an HTML string.

    Templates are loaded from the ``email-templates/build/`` directory
    relative to the ``app`` package.

    Args:
        template_name: Filename of the template (e.g. ``"test_email.html"``).
        context: Dictionary of variables to pass into the template.

    Returns:
        The rendered HTML string.
    """
    template_str = (
        Path(__file__).parent.parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """Send an email via SMTP using the application settings.

    Raises an ``AssertionError`` if email sending is not configured.

    Args:
        email_to: Recipient email address.
        subject: Email subject line.
        html_content: Rendered HTML body.
    """
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, cast(str, settings.EMAILS_FROM_EMAIL)),
    )
    smtp_options: dict[str, Any] = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
    }
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    """Generate a test email for verifying SMTP configuration.

    Args:
        email_to: Recipient email address.

    Returns:
        An :class:`EmailData` instance with the rendered test email.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """Generate a password-reset email containing a one-time link.

    Args:
        email_to: Recipient email address.
        email: The username / email displayed in the email body.
        token: JWT token embedded in the reset link.

    Returns:
        An :class:`EmailData` instance with the rendered reset email.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    """Generate a welcome email for a newly created account.

    Args:
        email_to: Recipient email address.
        username: The new user's login name.
        password: The new user's initial password.

    Returns:
        An :class:`EmailData` instance with the rendered welcome email.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


# ---------------------------------------------------------------------------
# JWT / password-reset tokens
# ---------------------------------------------------------------------------


def generate_password_reset_token(email: str) -> str:
    """Create a signed JWT for password-reset flows.

    The token contains ``exp``, ``nbf``, and ``sub`` claims and is signed
    with the application's ``SECRET_KEY``.

    Args:
        email: The user's email address, stored as the ``sub`` claim.

    Returns:
        The encoded JWT string.
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    """Decode and validate a password-reset JWT.

    Args:
        token: The JWT string to verify.

    Returns:
        The ``sub`` claim (email) if the token is valid, or ``None`` if
        verification fails.
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


# ---------------------------------------------------------------------------
# Datetime helpers
# ---------------------------------------------------------------------------


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime.

    Returns:
        A timezone-aware :class:`datetime.datetime` in UTC.
    """
    return datetime.now(UTC)
