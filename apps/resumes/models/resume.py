import uuid
from django.db import models
from apps.users.models import User

class Resume(models.Model):
    """
    Resume record. Storage is done in external provider; we store file_url + storage_key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=255)
    file_url = models.TextField()  # canonical URL (SAS or object URL)
    storage_key = models.CharField(max_length=1024)  # object key inside bucket/container
    file_size = models.BigIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=255, null=True, blank=True)
    original_filename = models.CharField(max_length=1024, null=True, blank=True)
    scan_status = models.CharField(max_length=32, default="pending")  # pending, scanning, clean, infected, unknown
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resumes"

    def __str__(self):
        return f"{self.user.email} - {self.title or self.original_filename or self.id}"
