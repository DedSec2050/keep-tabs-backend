# apps/resumes/services/storage/azure_storage.py
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from django.conf import settings

try:
    from azure.storage.blob import (
        BlobServiceClient,
        generate_blob_sas,
        BlobSasPermissions,
    )
except Exception as e:
    # allow import to fail in environments without azure libs; handle at runtime
    BlobServiceClient = None
    generate_blob_sas = None
    BlobSasPermissions = None

from .exceptions import ProviderConfigError, PresignError, UploadNotFoundError, DeleteError
from .utils import sanitize_filename, generate_storage_key

def _ensure_config():
    if not (settings.AZURE_ACCOUNT_NAME and settings.AZURE_ACCOUNT_KEY and settings.AZURE_CONTAINER):
        raise ProviderConfigError("Azure storage not configured properly.")

def presign_put(user, original_filename, content_type, expires=(PRESIGN_EXPIRY := settings.PRESIGNED_URL_EXPIRES)):
    _ensure_config()
    if generate_blob_sas is None:
        raise ProviderConfigError("azure-storage-blob package not installed")

    filename = sanitize_filename(original_filename or "resume")
    key = generate_storage_key(user.id, filename)

    try:
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_ACCOUNT_NAME,
            container_name=settings.AZURE_CONTAINER,
            blob_name=key,
            account_key=settings.AZURE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True, write=True, create=True),
            expiry=datetime.utcnow() + timedelta(seconds=expires),
        )
        blob_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER}/{quote_plus(key)}"
        upload_url = f"{blob_url}?{sas_token}"
    except Exception as e:
        raise PresignError("Failed to generate Azure SAS") from e

    return {"upload_url": upload_url, "blob_url": blob_url, "storage_key": key, "provider": "azure", "expires_in": expires}

def head_object(storage_key):
    _ensure_config()
    if BlobServiceClient is None:
        raise ProviderConfigError("azure-storage-blob package not installed")
    try:
        blob_service = BlobServiceClient(account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net", credential=settings.AZURE_ACCOUNT_KEY)
        container = settings.AZURE_CONTAINER
        blob_client = blob_service.get_blob_client(container=container, blob=storage_key)
        props = blob_client.get_blob_properties()
        return {
            "size": props.size,
            "content_type": props.content_settings.content_type,
            "url": f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{container}/{storage_key}"
        }
    except Exception as e:
        raise UploadNotFoundError("Azure object not found or inaccessible") from e

def delete_object(storage_key):
    _ensure_config()
    if BlobServiceClient is None:
        raise ProviderConfigError("azure-storage-blob package not installed")
    try:
        blob_service = BlobServiceClient(account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net", credential=settings.AZURE_ACCOUNT_KEY)
        container = settings.AZURE_CONTAINER
        blob_client = blob_service.get_blob_client(container=container, blob=storage_key)
        blob_client.delete_blob()
    except Exception as e:
        raise DeleteError("Failed to delete Azure object") from e
