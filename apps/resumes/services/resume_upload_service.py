# apps/resumes/services/resumes_upload_service.py
from django.conf import settings
from django.db import transaction
from apps.resumes.models import Resume
from .storage.manager import presign_put, head_object, delete_object
from .storage.exceptions import (
    ProviderConfigError, PresignError, UploadNotFoundError, VerificationError, DeleteError, StorageError
)
import logging

logger = logging.getLogger(__name__)

ALLOWED_MIMETYPES = set(settings.RESUME_ALLOWED_MIMETYPES or [])
MAX_BYTES = settings.RESUME_MAX_BYTES
PRESIGNED_EXPIRES = settings.PRESIGNED_URL_EXPIRES

def get_presigned_upload(user, original_filename, content_type, max_bytes=None):
    # Validation
    if content_type not in ALLOWED_MIMETYPES:
        raise ValueError("Content type not allowed")
    if max_bytes is not None and int(max_bytes) > MAX_BYTES:
        raise ValueError("File too large")

    try:
        res = presign_put(user, original_filename, content_type, expires=PRESIGNED_EXPIRES)
    except Exception as e:
        logger.exception("Presign generation failed")
        raise PresignError("Failed to generate presigned URL") from e

    # return upload instructions (upload_url, storage_key, blob_url, expires_in, provider)
    return res

@transaction.atomic
def finalize_upload(user, storage_key, title=None, original_filename=None, expected_size=None, expected_content_type=None):
    # verify object exists + metadata using storage provider
    try:
        meta = head_object(storage_key)
    except UploadNotFoundError as e:
        logger.warning("Finalize failed: object not found %s", storage_key)
        raise ValueError("Uploaded object not found") from e
    except Exception as e:
        logger.exception("Storage head_object failed")
        raise ValueError("Error while verifying uploaded object") from e

    size = meta.get("size")
    content_type = meta.get("content_type")
    url = meta.get("url")

    # verify expected size/type if provided
    if expected_size is not None:
        try:
            if int(expected_size) != int(size):
                raise VerificationError("Uploaded size mismatch")
        except ValueError:
            raise VerificationError("Invalid expected_size provided")
    if expected_content_type:
        # some providers may not preserve content-type on PUT; be slightly tolerant or keep strict based on policy
        if expected_content_type != content_type:
            raise VerificationError("Uploaded content-type mismatch")

    if size is not None and size > MAX_BYTES:
        raise VerificationError("Uploaded file too large")

    # Create DB record
    resume = Resume.objects.create(
        user=user,
        title=title or (original_filename or "Resume"),
        file_url=url,
        storage_key=storage_key,
        file_size=size,
        content_type=content_type,
        original_filename=original_filename,
        scan_status="pending",
    )

    # Hook: enqueue background virus scan task here (Celery/RQ). For now, we just set pending.
    logger.info("Resume uploaded and DB record created: %s", resume.id)

    return {
        "id": str(resume.id),
        "title": resume.title,
        "file_url": resume.file_url,
        "file_size": resume.file_size,
        "content_type": resume.content_type,
        "created_at": resume.created_at.isoformat(),
    }

def delete_resume_object_and_record(resume):
    """
    Delete object from storage and then delete DB record.
    Caller must ensure permission checks.
    """
    try:
        delete_object(resume.storage_key)
    except Exception as e:
        # Log but proceed to delete DB record? Policy choice:
        # We log the storage deletion failure and still delete DB record to avoid dangling UI items;
        # alternatively, return error and keep DB record. Here we keep robust: try storage delete, if fails raise.
        logger.exception("Failed to delete storage object %s", resume.storage_key)
        raise DeleteError("Failed to delete object from storage") from e

    resume.delete()
    return True
