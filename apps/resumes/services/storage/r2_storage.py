# # apps/resumes/services/storage/r2_storage.py
# from datetime import datetime, timedelta
# from urllib.parse import quote_plus
# from django.conf import settings

# import botocore
# import boto3
# from botocore.client import Config

# from .exceptions import ProviderConfigError, PresignError, UploadNotFoundError, DeleteError
# from .utils import sanitize_filename, generate_storage_key

# def _ensure_config():
#     if not (settings.R2_ENDPOINT_URL and settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY and settings.R2_BUCKET):
#         raise ProviderConfigError("R2 storage not configured properly")

# def _s3_client():
#     _ensure_config()
#     return boto3.client(
#         "s3",
#         endpoint_url=settings.R2_ENDPOINT_URL,
#         aws_access_key_id=settings.R2_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
#         config=Config(signature_version="s3v4"),
#     )

# def presign_put(user, original_filename, content_type, expires=settings.PRESIGNED_URL_EXPIRES):
#     _ensure_config()
#     s3 = _s3_client()
#     key = generate_storage_key(user.id, sanitize_filename(original_filename or "resume"))
#     try:
#         upload_url = s3.generate_presigned_url(
#             "put_object",
#             Params={"Bucket": settings.R2_BUCKET, "Key": key, "ContentType": content_type},
#             ExpiresIn=expires,
#             HttpMethod="PUT",
#         )
#         blob_url = f"{settings.R2_ENDPOINT_URL}/{settings.R2_BUCKET}/{quote_plus(key)}"
#     except Exception as e:
#         raise PresignError("Failed to generate R2 presigned URL") from e

#     return {"upload_url": upload_url, "blob_url": blob_url, "storage_key": key, "provider": "r2", "expires_in": expires}

# def head_object(storage_key):
#     s3 = _s3_client()
#     try:
#         head = s3.head_object(Bucket=settings.R2_BUCKET, Key=storage_key)
#         return {
#             "size": head["ContentLength"],
#             "content_type": head.get("ContentType"),
#             "url": f"{settings.R2_ENDPOINT_URL}/{settings.R2_BUCKET}/{storage_key}",
#         }
#     except botocore.exceptions.ClientError as e:
#         # 404 or other error -> treat as missing
#         raise UploadNotFoundError("R2 object not found or inaccessible") from e
#     except Exception as e:
#         raise UploadNotFoundError("R2 head_object failed") from e

# def delete_object(storage_key):
#     s3 = _s3_client()
#     try:
#         s3.delete_object(Bucket=settings.R2_BUCKET, Key=storage_key)
#     except Exception as e:
#         raise DeleteError("Failed to delete R2 object") from e
