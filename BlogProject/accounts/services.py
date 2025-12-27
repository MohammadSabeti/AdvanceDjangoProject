from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate_activation_token(user):
    """
    Generate a short-lived JWT access token for email activation.
    Note: This token is meant only for activation, not for API auth.
    """
    token = RefreshToken.for_user(user)
    # customize lifetime if needed
    token.set_exp(lifetime=settings.SIMPLE_JWT["ACTIVATION_TOKEN_LIFETIME"])
    return str(token.access_token)


def generate_reset_password_token(user):
    """
    Generate a short-lived JWT token for reset password.
    """
    payload = {
        "user_id": user.id,
        "type": "reset_password",
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
