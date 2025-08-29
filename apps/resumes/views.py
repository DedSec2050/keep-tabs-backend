from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from apps.users.authentication import users_allow_methods, users_require_json, users_authentication_required, users_active_required

from apps.resumes.services.resume_upload_service import (
    get_presigned_upload,
    finalize_upload,
    delete_resume_object_and_record,
)
from apps.resumes.models import Resume

import logging

logger = logging.getLogger(__name__)

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
@users_authentication_required
@users_active_required
def resumes_get_presigned_view(request):
    data = request.json
    original_filename = data.get("original_filename", "resume")
    content_type = data.get("content_type", "application/pdf")
    max_bytes = data.get("max_bytes")
    title = data.get("title")

    try:
        presigned = get_presigned_upload(request.user, original_filename, content_type, max_bytes)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.exception("Presign error")
        return JsonResponse({"error": "Failed to generate presigned URL"}, status=500)

    return JsonResponse({"upload": presigned, "title": title}, status=200)

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
@users_authentication_required
@users_active_required
def resumes_finalize_view(request):
    data = request.json
    storage_key = data.get("storage_key")
    title = data.get("title")
    original_filename = data.get("original_filename")
    expected_size = data.get("expected_size")
    expected_content_type = data.get("expected_content_type")

    if not storage_key:
        return JsonResponse({"error": "storage_key required"}, status=400)

    try:
        res = finalize_upload(
            request.user,
            storage_key,
            title=title,
            original_filename=original_filename,
            expected_size=expected_size,
            expected_content_type=expected_content_type,
        )
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.exception("Finalize upload failed")
        return JsonResponse({"error": "Failed to finalize upload"}, status=500)

    return JsonResponse({"message": "Upload finalized", "resume": res}, status=201)

@users_allow_methods(["GET"])
@csrf_exempt
@users_authentication_required
@users_active_required
def resumes_list_view(request):
    qs = request.user.resumes.all().order_by("-created_at")
    data = [
        {
            "id": str(r.id),
            "title": r.title,
            "file_url": r.file_url,
            "file_size": r.file_size,
            "content_type": r.content_type,
            "original_filename": r.original_filename,
            "scan_status": r.scan_status,
            "created_at": r.created_at.isoformat(),
        }
        for r in qs
    ]
    return JsonResponse({"resumes": data}, status=200)

@users_allow_methods(["DELETE"])
@users_require_json
@csrf_exempt
@users_authentication_required
@users_active_required
def resumes_delete_view(request):
    data = request.json
    resume_id = data.get("id")
    if not resume_id:
        return JsonResponse({"error": "id required"}, status=400)

    try:
        r = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)

    try:
        delete_resume_object_and_record(r)
    except Exception as e:
        logger.exception("Failed to delete resume %s", resume_id)
        return JsonResponse({"error": "Failed to delete resume"}, status=500)

    return JsonResponse({"message": "Deleted"}, status=200)
