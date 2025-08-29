from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

RESET_TOKEN_TTL_MINUTES = 15  # token valid for 15 mins

class PasswordResetToken(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reset_tokens")
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "user_password_reset_tokens"
        indexes = [models.Index(fields=["user", "created_at"])]

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at

    @classmethod
    def create_token(cls, user):
        cls.objects.filter(user=user).delete()  # cleanup old tokens
        token = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
        return cls.objects.create(user=user, token=token, expires_at=expires_at)
