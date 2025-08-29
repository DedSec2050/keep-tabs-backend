import json
from functools import wraps
from django.http import JsonResponse, HttpRequest
from apps.users.services.users_jwt_service import users_jwt_decode
from apps.users.models import User

def users_allow_methods(allowed):
    def deco(view):
        @wraps(view)
        def _wrap(request: HttpRequest, *args, **kwargs):
            if request.method not in allowed:
                return JsonResponse({"error": f"Method {request.method} not allowed"}, status=405)
            return view(request, *args, **kwargs)
        return _wrap
    return deco

def users_require_json(view):
    @wraps(view)
    def _wrap(request: HttpRequest, *args, **kwargs):
        if request.body:
            try:
                request.json = json.loads(request.body.decode("utf-8"))
            except Exception:
                return JsonResponse({"error": "Invalid JSON body"}, status=400)
        else:
            request.json = {}
        return view(request, *args, **kwargs)
    return _wrap

def users_authentication_required(view):
    @wraps(view)
    def _wrap(request: HttpRequest, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = users_jwt_decode(token)
        except Exception:
            return JsonResponse({"error": "Invalid or expired token"}, status=401)

        if payload.get("typ") != "access":
            return JsonResponse({"error": "Invalid token type"}, status=401)

        user_id = payload.get("sub")
        try:
            request.user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=401)

        return view(request, *args, **kwargs)
    return _wrap

def users_active_required(view):
    @wraps(view)
    def _wrap(request: HttpRequest, *args, **kwargs):
        user = getattr(request, "user", None)
        if not user or not user.active:
            return JsonResponse({"error": "Account inactive"}, status=403)
        return view(request, *args, **kwargs)
    return _wrap
