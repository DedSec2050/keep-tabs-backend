from django.db import models
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "user_otps"
        indexes = [models.Index(fields=["user", "created_at"])]

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at


class OTPThrottle(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="otp_throttle")
    last_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_otp_throttle"

    def can_send(self, min_interval_seconds: int) -> bool:
        if not self.last_sent_at:
            return True
        return timezone.now() >= self.last_sent_at + timedelta(seconds=min_interval_seconds)

    def mark_sent(self):
        self.last_sent_at = timezone.now()
        self.save(update_fields=["last_sent_at"])
