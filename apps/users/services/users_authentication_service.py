import hashlib
from django.db import transaction, IntegrityError
from apps.users.models import User
from apps.users.validators import (
    users_email_validate,
    users_username_validate,
    users_password_validate,
)
from .users_otp_service import users_otp_send

def _hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

@transaction.atomic
def users_register(data: dict) -> dict:
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    users_email_validate(email)
    users_username_validate(username)
    users_password_validate(password)

    try:
        user = User.objects.create(
            email=email,
            username=username,
            password_hash=_hash_password(password),
            active=False,
        )
    except IntegrityError:
        raise ValueError("A user with that email already exists.")

    users_otp_send(user)
    return {"id": user.id, "email": user.email, "username": user.username, "active": user.active}

def users_login(email: str, password: str) -> dict:
    email = (email or "").strip().lower()
    if not email or not password:
        raise ValueError("Email and password are required.")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValueError("Invalid credentials.")

    if user.password_hash != _hash_password(password):
        raise ValueError("Invalid credentials.")

    if not user.active:
        raise ValueError("Account is not active. Please verify OTP.")

    return {"user": user}
