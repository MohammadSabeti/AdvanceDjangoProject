import pytest
from django.urls import reverse

from accounts.models import Profile


@pytest.mark.django_db
class TestProfileApi:
    """End-to-end tests for ProfileApiView (RetrieveUpdateAPIView)."""

    def test_profile_anonymous_returns_404_or_401(self, api_client):
        """
        If ProfileApiView doesn't enforce IsAuthenticated,
        anonymous user may get 404 because get_object uses request.user.
        If you add IsAuthenticated later, it will become 401/403.
        """
        url = reverse("accounts:api-v1:profile")
        resp = api_client.get(url)
        assert resp.status_code in (401, 403, 404)

    def test_profile_authenticated_get_200(self, api_client, verified_user):
        """Authenticated user should retrieve their profile."""
        api_client.force_authenticate(user=verified_user)

        url = reverse("accounts:api-v1:profile")
        resp = api_client.get(url)

        assert resp.status_code == 200
        assert resp.data["email"] == verified_user.email
        assert resp.data["user_id"] == verified_user.id

    def test_profile_authenticated_patch_200(self, api_client, verified_user):
        """Authenticated user should be able to update profile fields."""
        api_client.force_authenticate(user=verified_user)

        # Ensure profile exists (signal or create)
        profile = getattr(verified_user, "profile", None) or Profile.objects.create(
            user=verified_user, first_name="A", last_name="B", description="D"
        )

        url = reverse("accounts:api-v1:profile")
        resp = api_client.patch(url, {"first_name": "Updated"}, format="json")

        assert resp.status_code == 200
        profile.refresh_from_db()
        assert profile.first_name == "Updated"
