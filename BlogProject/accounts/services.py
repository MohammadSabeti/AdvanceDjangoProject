from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

def generate_activation_token(user):
    """
    Generate a short-lived JWT access token for email activation.
    Note: This token is meant only for activation, not for API auth.
    """
    token = RefreshToken.for_user(user)
    # customize lifetime if needed
    token.set_exp(lifetime=settings.SIMPLE_JWT['ACTIVATION_TOKEN_LIFETIME'])
    return str(token.access_token)

