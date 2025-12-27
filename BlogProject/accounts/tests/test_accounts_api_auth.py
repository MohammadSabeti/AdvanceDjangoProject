import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token

from accounts.models import User


@pytest.mark.django_db
class TestRegistrationAndAuth:
    """
    End-to-end tests for:
    - Registration
    - DRF Token login/logout
    - JWT create/refresh/verify
    """

    def test_registration_creates_user_and_sends_email(
        self, api_client, mock_email_thread_start
    ):
        """
        Registration should:
        - create a user
        - send activation email (we mock EmailThread.start)
        - return 201 with {email: ...}
        """
        url = reverse("accounts:api-v1:registration")
        payload = {
            "email": "new@test.com",
            "password": "Pass12345/",
            "password1": "Pass12345/",
        }

        resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 201
        assert resp.data["email"] == "new@test.com"
        assert User.objects.filter(email="new@test.com").exists()
        assert mock_email_thread_start["count"] == 1

    def test_registration_password_mismatch_returns_400(
        self, api_client, mock_email_thread_start
    ):
        """Registration should return 400 if passwords do not match."""
        url = reverse("accounts:api-v1:registration")
        payload = {
            "email": "mismatch@test.com",
            "password": "Pass12345/",
            "password1": "Different12345/",
        }

        resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 400
        assert "detail" in resp.data
        assert mock_email_thread_start["count"] == 0

    def test_token_login_unverified_user_returns_400(self, api_client, user):
        """
        Token login must reject unverified users (CustomAuthTokenSerializer).
        """
        url = reverse("accounts:api-v1:token-login")
        payload = {"email": user.email, "password": "Pass12345/"}

        resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 400
        assert (
            "Unable to log in" in str(resp.data)
            or "not verified" in str(resp.data).lower()
        )

    def test_token_login_verified_user_returns_token(self, api_client, verified_user):
        """
        Verified user should obtain a DRF token and receive token + email fields.
        """
        url = reverse("accounts:api-v1:token-login")
        payload = {"email": verified_user.email, "password": "Pass12345/"}

        resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 200
        assert "token" in resp.data
        assert resp.data["email"] == verified_user.email
        assert Token.objects.filter(user=verified_user).exists()

    def test_token_logout_deletes_token_204(self, api_client, verified_user):
        """
        Logout should delete the user's token.
        Uses TokenAuthentication header: Authorization: Token <key>
        """
        token, _ = Token.objects.get_or_create(user=verified_user)

        url = reverse("accounts:api-v1:token-logout")
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        resp = api_client.post(url, {}, format="json")

        assert resp.status_code == 204
        assert not Token.objects.filter(user=verified_user).exists()

    def test_jwt_create_unverified_returns_400(self, api_client, user):
        """
        JWT obtain pair must reject unverified users (CustomTokenObtainPairSerializer).
        """
        url = reverse("accounts:api-v1:jwt-create")
        payload = {"email": user.email, "password": "Pass12345/"}

        resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 400
        assert "not verified" in str(resp.data).lower()

    def test_jwt_create_verified_returns_access_refresh(
        self, api_client, verified_user
    ):
        """
        Verified user should get access/refresh tokens and extra fields (email, user_id).
        """
        url = reverse("accounts:api-v1:jwt-create")
        payload = {"email": verified_user.email, "password": "Pass12345/"}

        resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data
        assert resp.data["email"] == verified_user.email
        assert resp.data["user_id"] == verified_user.id
