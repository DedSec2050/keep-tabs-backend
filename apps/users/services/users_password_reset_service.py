import random
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from apps.users.models import User, OTP, OTPThrottle
from apps.users.models.reset_password import PasswordResetToken
from apps.shared.services.email_service import EmailService

RESET_OTP_TTL_MINUTES = 10
RESET_OTP_RESEND_SECONDS = 60  # 1 minute cooldown

def _hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _throttle_for(user: User) -> OTPThrottle:
    throttle, _ = OTPThrottle.objects.get_or_create(user=user)
    return throttle

@transaction.atomic
def reset_password_request(email: str) -> None:
    email = (email or "").strip().lower()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValueError("No user found with this email.")

    throttle = _throttle_for(user)
    if not throttle.can_send(RESET_OTP_RESEND_SECONDS):
        raise ValueError(f"Please wait {RESET_OTP_RESEND_SECONDS} seconds before requesting another OTP.")

    OTP.objects.filter(user=user).delete()
    code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=RESET_OTP_TTL_MINUTES)
    OTP.objects.create(user=user, code=code, expires_at=expires_at)

    email_service = EmailService()
    email_service.send_email(
        sender_name="Keep Tabs",
        sender_email="marsal@200630.xyz",
        recipient_name=user.username,
        recipient_email=user.email,
        subject="Password Reset OTP",
        html_content=f"Your password reset OTP is {code}. It expires in {RESET_OTP_TTL_MINUTES} minutes.",
    )

    throttle.mark_sent()

def reset_password_verify(user: User, code: str) -> str:
    if not code or len(code) != 6:
        raise ValueError("Invalid OTP.")
    otp = OTP.objects.filter(user=user, code=code).order_by("-created_at").first()
    if not otp:
        raise ValueError("Incorrect OTP.")
    if not otp.is_valid():
        raise ValueError("OTP expired. Please request a new one.")

    OTP.objects.filter(user=user).delete()
    reset_token_obj = PasswordResetToken.create_token(user)
    return reset_token_obj.token

@transaction.atomic
def reset_password_confirm(email: str, token: str, new_password: str) -> None:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValueError("Invalid user.")

    reset_token = PasswordResetToken.objects.filter(user=user, token=token).order_by("-created_at").first()
    if not reset_token or not reset_token.is_valid():
        raise ValueError("Invalid or expired reset token.")

    user.password_hash = _hash_password(new_password)
    user.save(update_fields=["password_hash"])
    PasswordResetToken.objects.filter(user=user).delete()  # cleanup tokens
