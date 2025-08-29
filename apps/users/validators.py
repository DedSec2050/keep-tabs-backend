import re
from django.core.exceptions import ValidationError

def users_email_validate(email: str):
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError("Invalid email format.")

def users_username_validate(username: str):
    if not username or len(username) < 3:
        raise ValidationError("Username must be at least 3 characters.")

def users_password_validate(password: str):
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters.")
    if password.isalpha() or password.isdigit():
        raise ValidationError("Password must contain both letters and numbers.")
