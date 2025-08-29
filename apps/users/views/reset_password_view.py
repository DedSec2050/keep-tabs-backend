from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.users.authentication import users_allow_methods, users_require_json
from apps.users.services.users_password_reset_service import (
    reset_password_request,
    reset_password_verify,
    reset_password_confirm,
)
from apps.users.models import User

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def reset_password_request_view(request):
    email = (request.json.get("email") or "").strip().lower()
    try:
        reset_password_request(email)
        return JsonResponse({"message": "OTP sent to your email."})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def reset_password_verify_view(request):
    email = (request.json.get("email") or "").strip().lower()
    code = request.json.get("otp") or ""
    try:
        user = User.objects.get(email=email)
        token = reset_password_verify(user, code)
        return JsonResponse({"reset_token": token})
    except (User.DoesNotExist, ValueError) as e:
        return JsonResponse({"error": str(e)}, status=400)

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def reset_password_confirm_view(request):
    email = (request.json.get("email") or "").strip().lower()
    token = request.json.get("reset_token") or ""
    new_password = request.json.get("new_password") or ""
    try:
        reset_password_confirm(email, token, new_password)
        return JsonResponse({"message": "Password has been reset successfully."})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
