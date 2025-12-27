import pytest
from django.urls import reverse

from accounts.models import User
from accounts.services import generate_activation_token


@pytest.mark.django_db
class TestActivationFlow:
    """End-to-end tests for activation confirm + resend endpoints."""

    def test_activation_confirm_success_marks_verified(self, api_client):
        """Activation endpoint should set is_verified=True for a valid token."""
        user = User.objects.create_user(email="act@test.com", password="Pass12345/")
        assert user.is_verified is False

        token = generate_activation_token(user)
        url = reverse("accounts:api-v1:activation", kwargs={"token": token})

        resp = api_client.get(url)

        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.is_verified is True

    def test_activation_confirm_already_verified_returns_message(self, api_client):
        """If user is already verified, activation should return a friendly message."""
        user = User.objects.create_user(email="act2@test.com", password="Pass12345/")
        user.is_verified = True
        user.save()

        token = generate_activation_token(user)
        url = reverse("accounts:api-v1:activation", kwargs={"token": token})

        resp = api_client.get(url)

        assert resp.status_code == 200
        assert "already" in str(resp.data).lower()

    def test_activation_resend_nonexistent_user_returns_400(
        self, api_client, mock_email_thread_start
    ):
        """Resend should return 400 if user does not exist."""
        url = reverse("accounts:api-v1:activation-resend")

        resp = api_client.post(url, {"email": "missing@test.com"}, format="json")

        assert resp.status_code == 400
        assert mock_email_thread_start["count"] == 0

    def test_activation_resend_verified_user_returns_400(
        self, api_client, mock_email_thread_start
    ):
        """Resend should return 400 if user is already verified."""
        user = User.objects.create_user(email="v2@test.com", password="Pass12345/")
        user.is_verified = True
        user.save()

        url = reverse("accounts:api-v1:activation-resend")
        resp = api_client.post(url, {"email": user.email}, format="json")

        assert resp.status_code == 400
        assert mock_email_thread_start["count"] == 0

    def test_activation_resend_unverified_user_sends_email_200(
        self, api_client, mock_email_thread_start
    ):
        """Resend should send email for unverified user and return 200."""
        user = User.objects.create_user(email="u3@test.com", password="Pass12345/")
        assert user.is_verified is False

        url = reverse("accounts:api-v1:activation-resend")
        resp = api_client.post(url, {"email": user.email}, format="json")

        assert resp.status_code == 200
        assert mock_email_thread_start["count"] == 1
