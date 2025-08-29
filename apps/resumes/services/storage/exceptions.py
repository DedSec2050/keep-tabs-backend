# apps/resumes/services/storage/exceptions.py
class StorageError(Exception):
    """Generic storage error"""

class ProviderConfigError(StorageError):
    """Provider not configured properly"""

class PresignError(StorageError):
    """Failed to generate presigned URL"""

class UploadNotFoundError(StorageError):
    """Uploaded object not found in storage"""

class VerificationError(StorageError):
    """Uploaded object failed verification (size/content-type mismatch)"""

class DeleteError(StorageError):
    """Failed to delete object from storage"""
