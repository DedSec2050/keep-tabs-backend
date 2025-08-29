from django.http import JsonResponse
from apps.users.authentication import users_allow_methods, users_require_json
from apps.users.services.users_otp_service import users_otp_send, users_otp_verify
from apps.users.models import User
from django.views.decorators.csrf import csrf_exempt

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def users_otp_resend_view(request):
    email = (request.json.get("email") or "").strip().lower()
    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)
    try:
        user = User.objects.get(email=email)
        if user.active:
            return JsonResponse({"error": "Account already active"}, status=400)
        users_otp_send(user)
        return JsonResponse({"message": "OTP resent. Check your email."})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except ValueError as e:
        # Throttled
        return JsonResponse({"error": str(e)}, status=429)

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def users_otp_verify_view(request):
    email = (request.json.get("email") or "").strip().lower()
    code = (request.json.get("otp") or "").strip()
    if not email or not code:
        return JsonResponse({"error": "Email and otp are required"}, status=400)
    try:
        user = User.objects.get(email=email)
        if user.active:
            return JsonResponse({"message": "Account already active"}, status=200)
        users_otp_verify(user, code)
        return JsonResponse({"message": "OTP verified. Account activated."})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
