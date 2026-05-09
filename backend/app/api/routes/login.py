from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)
from app.model.other import Message, Token
from app.model.user import (
    ForcePasswordResetRequest,
    NewPassword,
    User,
    UserPublic,
    UserUpdate,
)
from app.service import crud

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="The email or password provided is incorrect. Please double-check and try again.",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="This account is currently inactive. Please contact support for assistance.",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token.
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password recovery. Always return the same response to prevent email enumeration attacks. Only send email if user actually exists.
    """
    user = crud.get_user_by_email(session=session, email=email)
    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return Message(
        message="If an account exists for that email, a password recovery link has been sent. Please check your inbox and spam folder.",
        success=True,
        status="Success",
        code=200,
    )


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password. Don't reveal that the user doesn't exist - use same error as invalid token.
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="The password reset token is invalid or has expired.",
        )
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="The password reset token is invalid or has expired.",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="This account is currently inactive. Please contact support for assistance.",
        )
    user_in_update = UserUpdate(password=body.new_password)
    crud.update_user(
        session=session,
        db_user=user,
        user_in=user_in_update,
    )
    return Message(
        message="Your password has been updated successfully. You can now log in.",
        success=True,
        status="Success",
        code=200,
    )


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML content for password recovery.
    """
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="We could not find a user with the provided email address in our system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )


@router.post(
    "/login/force-password-reset",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def force_password_reset_for_users(
    session: SessionDep, body: ForcePasswordResetRequest
) -> Message:
    """
    Force password reset for a targeted list of users or all active users.
    """
    if not body.emails and not body.include_all_active_users:
        raise HTTPException(
            status_code=400,
            detail="Provide emails or set include_all_active_users=true.",
        )
    users_by_id: dict[str, User] = {}
    if body.include_all_active_users:
        active_users = session.exec(
            select(User).where(col(User.is_active).is_(True))
        ).all()
        users_by_id.update({str(user.id): user for user in active_users})
    if body.emails:
        targetedUsers = session.exec(
            select(User).where(col(User.email).in_(body.emails))
        ).all()
        users_by_id.update({str(user.id): user for user in targetedUsers})
    flagged_count = 0
    for user in users_by_id.values():
        if user.force_password_reset:
            continue
        user.force_password_reset = True
        session.add(user)
        flagged_count += 1
    session.commit()
    return Message(
        message=f"Successfully forced password reset for {flagged_count} user(s) out of {len(users_by_id)} targeted account(s).",
        success=True,
        status="Success",
        code=200,
    )
