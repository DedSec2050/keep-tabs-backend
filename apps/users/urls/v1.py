from django.urls import path
from apps.users.views import (
    users_register_view,
    users_otp_resend_view,
    users_otp_verify_view,
    users_login_view,
    users_token_refresh_view,
    users_logout_view,
    reset_password_request_view,
    reset_password_verify_view,
    reset_password_confirm_view,
)

urlpatterns = [
    path("register/", users_register_view, name="users_register"),
    path("otp/resend/", users_otp_resend_view, name="users_otp_resend"),
    path("otp/verify/", users_otp_verify_view, name="users_otp_verify"),
    path("login/", users_login_view, name="users_login"),
    path("token/refresh/", users_token_refresh_view, name="users_token_refresh"),
    path("logout/", users_logout_view, name="users_logout"),
    path("reset-password/request/", reset_password_request_view, name="reset_password_request"),
    path("reset-password/verify/", reset_password_verify_view, name="reset_password_verify"),
    path("reset-password/confirm/", reset_password_confirm_view, name="reset_password_confirm"),

]
