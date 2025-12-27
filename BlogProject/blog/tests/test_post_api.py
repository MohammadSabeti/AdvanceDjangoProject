import pytest
from django.urls import reverse
from django.utils import timezone


# ============================================================
# API Tests (Behavior & Permissions)
# ============================================================

@pytest.mark.django_db
class TestPostApi:
    """
    End-to-end API tests for PostViewSet.

    These tests verify:
    - Public read access
    - Authentication requirements
    - Owner-based permissions
    - Serializer output differences between list and detail views
    """

    def test_list_posts_is_public_200(self, api_client):
        """
        Anonymous users should be able to list posts.
        (IsAuthenticatedOrReadOnly allows SAFE_METHODS)
        """
        url = reverse("blog:api-v1:post-list")
        response = api_client.get(url)

        assert response.status_code == 200

    def test_retrieve_post_is_public_200(self, api_client, post):
        """
        Anonymous users should be able to retrieve a single post.
        """
        url = reverse(
            "blog:api-v1:post-detail",
            kwargs={"pk": post.id},
        )
        response = api_client.get(url)

        assert response.status_code == 200

    def test_create_post_requires_authentication(self, api_client, category):
        """
        Creating a post without authentication should be rejected.
        Depending on authentication configuration, DRF may return 401 or 403,
        but the error message must indicate missing credentials.
        """
        url = reverse("blog:api-v1:post-list")
        data = {
            "title": "New post",
            "content": "Post content",
            "status": True,
            "category": category.name,
            "published_date": timezone.now(),
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code in (401, 403)
        assert "Authentication credentials" in str(response.data)

    def test_create_post_authenticated_201(self, api_client, user, category):
        """
        An authenticated user should be able to create a post.
        The author field must be set automatically from request.user.profile.
        """
        api_client.force_authenticate(user=user)

        url = reverse("blog:api-v1:post-list")
        data = {
            "title": "New post",
            "content": "Hello. Second sentence!",
            "status": True,
            "category": category.name,
            "published_date": timezone.now(),
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 201
        assert response.data["author"]
        assert response.data["category"]["name"] == category.name

    def test_create_post_invalid_category_returns_400(self, api_client, user):
        """
        Serializer should return 400 if the category slug does not exist.
        """
        api_client.force_authenticate(user=user)

        url = reverse("blog:api-v1:post-list")
        data = {
            "title": "Invalid category",
            "content": "Content",
            "category": "non-existent-category",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert "category" in response.data

    def test_list_representation_hides_content(self, api_client, post):
        """
        In list view:
        - 'content' must be removed
        - 'brief_content' must be present
        """
        url = reverse("blog:api-v1:post-list")
        response = api_client.get(url)

        assert response.status_code == 200
        item = response.data["results"][0]

        assert "content" not in item
        assert "brief_content" in item

    def test_detail_representation_includes_content(self, api_client, post):
        """
        In detail view:
        - 'content' must be present
        - 'brief_content', 'relative_url', and 'absolute_url' must be removed
        """
        url = reverse(
            "blog:api-v1:post-detail",
            kwargs={"pk": post.id},
        )
        response = api_client.get(url)

        assert response.status_code == 200
        assert "content" in response.data
        assert "brief_content" not in response.data
        assert "relative_url" not in response.data
        assert "absolute_url" not in response.data

    def test_update_post_by_owner_returns_200(self, api_client, user, post):
        """
        The owner of a post should be able to update it.
        """
        api_client.force_authenticate(user=user)

        url = reverse(
            "blog:api-v1:post-detail",
            kwargs={"pk": post.id},
        )
        response = api_client.patch(
            url,
            {"title": "Updated title"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["title"] == "Updated title"

    def test_update_post_by_non_owner_returns_403(self, api_client, other_user, post):
        """
        A non-owner user must not be allowed to update the post.
        """
        api_client.force_authenticate(user=other_user)

        url = reverse(
            "blog:api-v1:post-detail",
            kwargs={"pk": post.id},
        )
        response = api_client.patch(
            url,
            {"title": "Hacked"},
            format="json",
        )

        assert response.status_code == 403

    def test_delete_post_by_owner_returns_204(self, api_client, user, post):
        """
        The owner of a post should be able to delete it.
        """
        api_client.force_authenticate(user=user)

        url = reverse(
            "blog:api-v1:post-detail",
            kwargs={"pk": post.id},
        )
        response = api_client.delete(url)

        assert response.status_code == 204

    def test_get_ok_action_returns_200(self, api_client):
        """
        Custom action `get_ok` should be publicly accessible
        and return a simple health-check response.
        """
        url = reverse("blog:api-v1:post-get-ok")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data == {"detail": "ok"}
