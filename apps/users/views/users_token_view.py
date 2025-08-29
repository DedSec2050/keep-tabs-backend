from django.http import JsonResponse
from apps.users.authentication import (
    users_allow_methods,
    users_require_json,
    users_authentication_required,
    users_active_required,
)
from apps.users.services.users_token_service import users_token_refresh, users_token_revoke
from django.views.decorators.csrf import csrf_exempt 

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def users_token_refresh_view(request):
    refresh = request.json.get("refresh") or ""
    if not refresh:
        return JsonResponse({"error": "Refresh token is required"}, status=400)
    try:
        new_tokens = users_token_refresh(refresh)
        return JsonResponse(new_tokens)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

@users_allow_methods(["POST"])
@users_require_json
@users_authentication_required
@users_active_required
@csrf_exempt
def users_logout_view(request):
    refresh = request.json.get("refresh") or ""
    if not refresh:
        return JsonResponse({"error": "Refresh token is required"}, status=400)
    try:
        users_token_revoke(refresh)
        return JsonResponse({"message": "Logged out"})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
