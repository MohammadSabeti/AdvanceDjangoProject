import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.services import generate_reset_password_token

User = get_user_model()


@pytest.mark.django_db
class TestPasswordFlows:
    """End-to-end tests for password change and reset flow."""

    def test_change_password_requires_auth(self, api_client):
        """Change password must require authentication."""
        url = reverse("accounts:api-v1:change-password")
        payload = {
            "old_password": "x",
            "new_password": "Pass12345/",
            "new_password1": "Pass12345/",
        }

        resp = api_client.put(url, payload, format="json")
        assert resp.status_code in (401, 403)

    def test_change_password_wrong_old_password_returns_400(
        self, api_client, verified_user
    ):
        """Wrong old password should return 400 with old_password error."""
        api_client.force_authenticate(user=verified_user)

        url = reverse("accounts:api-v1:change-password")
        payload = {
            "old_password": "wrong",
            "new_password": "NewPass12345/",
            "new_password1": "NewPass12345/",
        }

        resp = api_client.put(url, payload, format="json")

        assert resp.status_code == 400
        assert "old_password" in resp.data

    def test_change_password_success_200_and_password_updates(
        self, api_client, verified_user
    ):
        """Valid request should update password and return 200 success structure."""
        api_client.force_authenticate(user=verified_user)

        url = reverse("accounts:api-v1:change-password")
        payload = {
            "old_password": "Pass12345/",
            "new_password": "NewPass12345/",
            "new_password1": "NewPass12345/",
        }

        resp = api_client.put(url, payload, format="json")

        assert resp.status_code == 200
        verified_user.refresh_from_db()
        assert verified_user.check_password("NewPass12345/")

    def test_reset_password_request_always_200(
        self, api_client, verified_user, mock_email_thread_start
    ):
        """
        Reset password request must always return 200 to avoid user enumeration.
        If the email exists, it should trigger sending an email (mocked).
        """
        url = reverse("accounts:api-v1:reset-password")

        # Existing user -> should send email
        resp1 = api_client.post(url, {"email": verified_user.email}, format="json")
        assert resp1.status_code == 200
        assert mock_email_thread_start["count"] == 1

        # Non-existing user -> still 200, no email should be sent
        resp2 = api_client.post(url, {"email": "nope@test.com"}, format="json")
        assert resp2.status_code == 200
        assert mock_email_thread_start["count"] == 1  # unchanged

    def test_reset_password_confirm_invalid_token_400(self, api_client):
        """Invalid token must return 400."""
        url = reverse(
            "accounts:api-v1:reset-password-confirm",
            kwargs={"token": "invalid.token.value"},
        )
        resp = api_client.post(
            url,
            {"password": "NewPass12345/", "password1": "NewPass12345/"},
            format="json",
        )
        assert resp.status_code == 400

    def test_reset_password_confirm_success_200_and_password_updates(
        self, api_client, verified_user
    ):
        """Valid reset token should allow setting a new password."""
        token = generate_reset_password_token(verified_user)
        url = reverse("accounts:api-v1:reset-password-confirm", kwargs={"token": token})

        resp = api_client.post(
            url,
            {"password": "NewPass12345/", "password1": "NewPass12345/"},
            format="json",
        )

        assert resp.status_code == 200
        verified_user.refresh_from_db()
        assert verified_user.check_password("NewPass12345/")
