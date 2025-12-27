import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from accounts.models import User
from blog.models import Category, Post

# ============================================================
# Fixtures (Arrange layer)
# ============================================================

@pytest.fixture
def api_client():
    """Return a DRF APIClient instance."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a regular user."""
    return User.objects.create_user(
        email="u1@test.com",
        password="pass12345/",
    )


@pytest.fixture
def other_user(db):
    """Create another user (used for permission tests)."""
    return User.objects.create_user(
        email="u2@test.com",
        password="pass12345/",
    )


@pytest.fixture
def profile(user):
    """
    Return the profile associated with the user.
    Assumes Profile is automatically created via signals.
    """
    profile = user.profile
    profile.first_name = "John"
    profile.last_name = "Doe"
    profile.description = "Test profile"
    profile.save()
    return profile


@pytest.fixture
def other_profile(other_user):
    """Return the profile of the second user."""
    profile = other_user.profile
    profile.first_name = "Jane"
    profile.last_name = "Doe"
    profile.description = "Other profile"
    profile.save()
    return profile


@pytest.fixture
def category(db):
    """Create a blog category."""
    return Category.objects.create(name="Test Category")


@pytest.fixture
def post(db, profile, category):
    """Create a published blog post owned by `profile`."""
    return Post.objects.create(
        title="First post",
        content="Hello world. Second sentence!",
        author=profile,
        status=True,
        category=category,
        published_date=timezone.now(),
    )
