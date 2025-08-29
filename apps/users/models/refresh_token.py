from django.db import models
from django.utils import timezone

class UsersRefreshToken(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="refresh_tokens")
    token = models.CharField(max_length=512, unique=True)  # signed refresh token string
    jti = models.CharField(max_length=64, unique=True)     # token id to revoke/check
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_refresh_tokens"
        indexes = [
            models.Index(fields=["user", "expires_at"]),
            models.Index(fields=["jti"]),
        ]

    def is_active(self) -> bool:
        return (not self.revoked) and (timezone.now() < self.expires_at)
