from django.http import JsonResponse
from apps.users.authentication import users_allow_methods, users_require_json
from apps.users.services.users_authentication_service import users_login
from apps.users.services.users_token_service import users_token_generate_pair
from django.views.decorators.csrf import csrf_exempt

@users_allow_methods(["POST"])
@users_require_json
@csrf_exempt
def users_login_view(request):
    email = (request.json.get("email") or "").strip().lower()
    password = request.json.get("password") or ""
    try:
        result = users_login(email, password)
        user = result["user"]
        tokens = users_token_generate_pair(user)
        return JsonResponse({"access": tokens["access"], "refresh": tokens["refresh"]})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
