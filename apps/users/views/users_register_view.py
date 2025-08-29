from django.http import JsonResponse
from apps.users.authentication import users_allow_methods, users_require_json
from apps.users.services.users_authentication_service import users_register
from django.views.decorators.csrf import csrf_exempt

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def users_register_view(request):
    try:
        result = users_register(request.json)
        return JsonResponse({"message": "Registered. OTP sent to email.", "user": result}, status=201)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

