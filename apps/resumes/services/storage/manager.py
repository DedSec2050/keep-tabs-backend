from django.conf import settings
from .exceptions import ProviderConfigError, PresignError, UploadNotFoundError, DeleteError

# lazy imports to avoid import-time errors
def _get_provider_module():
    provider = (settings.STORAGE_PROVIDER or "azure").lower()
    if provider == "azure":
        from . import azure_storage as provider_mod
    elif provider in ("r2", "cloudflare", "r2_cloudflare"):
        from . import r2_storage as provider_mod
    else:
        raise ProviderConfigError(f"Unsupported storage provider: {provider}")
    return provider_mod

def presign_put(user, original_filename, content_type, expires=None):
    mod = _get_provider_module()
    try:
        return mod.presign_put(user, original_filename, content_type, expires=expires or settings.PRESIGNED_URL_EXPIRES)
    except Exception as e:
        # map provider exceptions to unified PresignError if not already
        raise

def head_object(storage_key):
    mod = _get_provider_module()
    return mod.head_object(storage_key)

def delete_object(storage_key):
    mod = _get_provider_module()
    return mod.delete_object(storage_key)
