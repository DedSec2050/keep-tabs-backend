import random
from datetime import timedelta
from django.utils import timezone
from apps.users.models import OTP, OTPThrottle, User
from apps.shared.services.email_service import EmailService
from django.views.decorators.csrf import csrf_exempt

OTP_TTL_MINUTES = 10
OTP_RESEND_SECONDS = 5

def _throttle_for(user: User) -> OTPThrottle:
    throttle, _ = OTPThrottle.objects.get_or_create(user=user)
    return throttle

def users_otp_send(user: User) -> None:
    throttle = _throttle_for(user)
    if not throttle.can_send(OTP_RESEND_SECONDS):
        raise ValueError(f"Please wait {OTP_RESEND_SECONDS} seconds before requesting another OTP.")

    OTP.objects.filter(user=user).delete()

    code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)
    OTP.objects.create(user=user, code=code, expires_at=expires_at)

    email_service = EmailService()
    email_service.send_email(
        sender_name="Keep Tabs",
        sender_email="marsal@200630.xyz",
        recipient_name=user.username,
        recipient_email=user.email,
        subject="Your OTP Code",
        html_content=f"Your OTP is {code}. It expires in {OTP_TTL_MINUTES} minutes.",
    )
    print("OTP sent successfully: " + code)

    throttle.mark_sent()

@csrf_exempt
def users_otp_verify(user: User, code: str) -> None:
    if not code or len(code) != 6:
        raise ValueError("Invalid OTP.")
    otp = OTP.objects.filter(user=user, code=code).order_by("-created_at").first()
    if not otp:
        raise ValueError("Incorrect OTP.")
    if not otp.is_valid():
        raise ValueError("OTP expired. Please request a new one.")

    user.active = True
    user.save(update_fields=["active"])
    OTP.objects.filter(user=user).delete()
