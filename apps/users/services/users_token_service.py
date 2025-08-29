import os
import time
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from apps.users.models import UsersRefreshToken, User
from .users_jwt_service import users_jwt_encode, users_jwt_decode

# lifetimes
ACCESS_TTL_SEC = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))      # 15 min
REFRESH_TTL_SEC = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "604800")) # 7 days

def users_token_generate_pair(user: User) -> dict:
    now = int(time.time())
    access_payload = {
        "sub": str(user.id),
        "typ": "access",
        "iat": now,
        "exp": now + ACCESS_TTL_SEC,
        "email": user.email,
        "username": user.username,
        "active": bool(user.active),
    }
    access = users_jwt_encode(access_payload)

    jti = uuid.uuid4().hex
    refresh_payload = {
        "sub": str(user.id),
        "typ": "refresh",
        "iat": now,
        "exp": now + REFRESH_TTL_SEC,
        "jti": jti,
    }
    refresh = users_jwt_encode(refresh_payload)

    # persist refresh token
    UsersRefreshToken.objects.create(
        user=user,
        token=refresh,
        jti=jti,
        expires_at=timezone.now() + timedelta(seconds=REFRESH_TTL_SEC),
        revoked=False,
    )

    return {"access": access, "refresh": refresh}

def users_token_refresh(refresh_token: str) -> dict:
    # Verify signature & exp
    payload = users_jwt_decode(refresh_token)
    if payload.get("typ") != "refresh":
        raise ValueError("Invalid refresh token type")

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise ValueError("Malformed refresh token")

    # Check DB entry
    try:
        db_token = UsersRefreshToken.objects.get(jti=jti, token=refresh_token)
    except UsersRefreshToken.DoesNotExist:
        raise ValueError("Refresh token not recognized")

    if not db_token.is_active():
        raise ValueError("Refresh token expired or revoked")

    # Issue new access token only (rotation optional)
    user = User.objects.get(id=sub)
    if not user.active:
        raise ValueError("Inactive account")

    now = int(time.time())
    access_payload = {
        "sub": str(user.id),
        "typ": "access",
        "iat": now,
        "exp": now + ACCESS_TTL_SEC,
        "email": user.email,
        "username": user.username,
        "active": True,
    }
    access = users_jwt_encode(access_payload)
    return {"access": access}

def users_token_revoke(refresh_token: str) -> None:
    try:
        payload = users_jwt_decode(refresh_token)
        jti = payload.get("jti")
        if not jti:
            raise ValueError("Malformed refresh token")
        db_token = UsersRefreshToken.objects.get(jti=jti, token=refresh_token)
        db_token.revoked = True
        db_token.save(update_fields=["revoked"])
    except Exception:
        # Hide details to client
        raise ValueError("Invalid refresh token")
