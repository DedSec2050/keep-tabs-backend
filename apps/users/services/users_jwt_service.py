import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Any
from django.conf import settings

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def _sign(message: bytes, secret: str) -> str:
    sig = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(sig)

def users_jwt_encode(payload: Dict[str, Any], secret: str = None) -> str:
    if secret is None:
        secret = settings.SECRET_KEY
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{h_b64}.{p_b64}".encode("ascii")
    sig_b64 = _sign(signing_input, secret)
    return f"{h_b64}.{p_b64}.{sig_b64}"

def users_jwt_decode(token: str, secret: str = None) -> Dict[str, Any]:
    if secret is None:
        secret = settings.SECRET_KEY
    try:
        h_b64, p_b64, s_b64 = token.split(".")
        signing_input = f"{h_b64}.{p_b64}".encode("ascii")
        expected = _sign(signing_input, secret)
        if not hmac.compare_digest(expected, s_b64):
            raise ValueError("Invalid signature")
        payload = json.loads(_b64url_decode(p_b64))
        # Optional exp check
        exp = payload.get("exp")
        if exp and int(time.time()) >= int(exp):
            raise ValueError("Token expired")
        return payload
    except Exception as e:
        raise ValueError("Invalid token") from e
