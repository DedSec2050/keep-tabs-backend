# apps/resumes/urls/v1.py
from django.urls import path
from apps.resumes.views import (
    resumes_get_presigned_view,
    resumes_finalize_view,
    resumes_list_view,
    resumes_delete_view,
)

urlpatterns = [
    path("upload/presign/", resumes_get_presigned_view, name="resumes_presign"),
    path("upload/finalize/", resumes_finalize_view, name="resumes_finalize"),
    path("", resumes_list_view, name="resumes_list"),
    path("delete/", resumes_delete_view, name="resumes_delete"),
]
