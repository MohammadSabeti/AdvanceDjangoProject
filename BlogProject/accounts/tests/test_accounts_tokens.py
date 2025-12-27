import jwt
import pytest
from django.conf import settings

from accounts.models import User
from accounts.services import (
    generate_activation_token,
    generate_reset_password_token,
)


@pytest.mark.django_db
class TestTokenHelpers:
    """Tests for token helper functions."""

    def test_generate_activation_token_returns_jwt_like_string(self):
        """Activation token should look like a JWT (three dot-separated parts)."""
        user = User.objects.create_user(email="u@test.com", password="Pass12345/")
        token = generate_activation_token(user)
        assert isinstance(token, str)
        assert token.count(".") == 2  # header.payload.signature

    def test_generate_reset_password_token_decodes_and_has_expected_payload(
        self,
    ):
        """Reset-password token should decode and contain correct payload structure."""
        user = User.objects.create_user(email="u2@test.com", password="Pass12345/")
        token = generate_reset_password_token(user)

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["user_id"] == user.id
        assert decoded["type"] == "reset_password"
        assert "exp" in decoded
