import pytest
from django.urls import reverse

from blog.models import Category


# ============================================================
# API Tests (Behavior & Permissions)
# ============================================================

@pytest.mark.django_db
class TestCategoryApi:
    """
    End-to-end API tests for CategoryViewSet.

    These tests verify:
    - Public read access (list/retrieve)
    - Authentication requirements for write actions (create/update/delete)
    - Basic serializer validation behavior
    """

    def test_list_categories_is_public_200(self, api_client, category):
        """
        Anonymous users should be able to list categories.
        (IsAuthenticatedOrReadOnly allows SAFE_METHODS)
        """
        url = reverse("blog:api-v1:category-list")
        response = api_client.get(url)

        assert response.status_code == 200

        # DefaultRouter list usually returns a list (no pagination unless configured globally)
        assert isinstance(response.data, list)
        assert any(item["name"] == category.name for item in response.data)

    def test_retrieve_category_is_public_200(self, api_client, category):
        """
        Anonymous users should be able to retrieve a single category.
        """
        url = reverse("blog:api-v1:category-detail", kwargs={"pk": category.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == category.id
        assert response.data["name"] == category.name

    def test_create_category_requires_authentication(self, api_client):
        """
        Creating a category without authentication should be rejected.
        Depending on authentication configuration, DRF may return 401 or 403,
        but the error message must indicate missing credentials.
        """
        url = reverse("blog:api-v1:category-list")
        response = api_client.post(url, {"name": "Science"}, format="json")

        assert response.status_code in (401, 403)
        assert "Authentication credentials" in str(response.data)

    def test_create_category_authenticated_201(self, api_client, user):
        """
        An authenticated user should be able to create a category.
        """
        api_client.force_authenticate(user=user)

        url = reverse("blog:api-v1:category-list")
        response = api_client.post(url, {"name": "Science"}, format="json")

        assert response.status_code == 201
        assert response.data["name"] == "Science"
        assert "id" in response.data

    def test_create_category_invalid_payload_400(self, api_client, user):
        """
        Serializer should return 400 when required fields are missing.
        """
        api_client.force_authenticate(user=user)

        url = reverse("blog:api-v1:category-list")
        response = api_client.post(url, {}, format="json")

        assert response.status_code == 400
        assert "name" in response.data

    def test_update_category_requires_authentication(self, api_client, category):
        """
        Updating a category without authentication should be rejected.
        """
        url = reverse("blog:api-v1:category-detail", kwargs={"pk": category.id})
        response = api_client.patch(url, {"name": "Updated"}, format="json")

        assert response.status_code in (401, 403)
        assert "Authentication credentials" in str(response.data)

    def test_update_category_authenticated_200(self, api_client, user, category):
        """
        An authenticated user should be able to update a category.
        """
        api_client.force_authenticate(user=user)

        url = reverse("blog:api-v1:category-detail", kwargs={"pk": category.id})
        response = api_client.patch(url, {"name": "Updated"}, format="json")

        assert response.status_code == 200
        assert response.data["name"] == "Updated"

    def test_delete_category_requires_authentication(self, api_client, category):
        """
        Deleting a category without authentication should be rejected.
        """
        url = reverse("blog:api-v1:category-detail", kwargs={"pk": category.id})
        response = api_client.delete(url)

        assert response.status_code in (401, 403)
        assert "Authentication credentials" in str(response.data)

    def test_delete_category_authenticated_204(self, api_client, user, category):
        """
        An authenticated user should be able to delete a category.
        """
        api_client.force_authenticate(user=user)

        url = reverse("blog:api-v1:category-detail", kwargs={"pk": category.id})
        response = api_client.delete(url)

        assert response.status_code == 204

        # Verify it is really deleted
        assert not Category.objects.filter(id=category.id).exists()
