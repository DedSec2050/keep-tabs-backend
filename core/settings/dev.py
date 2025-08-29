from .base import *
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

DEBUG = True
ALLOWED_HOSTS = ['*']

try:
    BREVO_API_KEY = os.environ["BREVO_API_KEY"]
    print("ENVIRONMENT SET TO DEV!!")
except KeyError:
    print("ENV_KEYS is not set in the environment.")
    BREVO_API_KEY = ""




STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "azure").lower()  # "azure" or "r2"

# Azure Blob Storage
AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME", "")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY", "")
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER", "resumes")

# Cloudflare R2 (S3-compatible)
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET = os.getenv("R2_BUCKET", "resumes")

# Upload constraints
RESUME_MAX_BYTES = int(os.getenv("RESUME_MAX_BYTES", 5 * 1024 * 1024))  # default 5MB
RESUME_ALLOWED_MIMETYPES = os.getenv(
    "RESUME_ALLOWED_MIMETYPES",
    "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
).split(",")
PRESIGNED_URL_EXPIRES = int(os.getenv("PRESIGNED_URL_EXPIRES", 300))  # seconds
