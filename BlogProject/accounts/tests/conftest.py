import pytest
from rest_framework.test import APIClient
from accounts.models import User


@pytest.fixture
def api_client():
    """DRF API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Unverified user by default."""
    return User.objects.create_user(email="u@test.com", password="Pass12345/")


@pytest.fixture
def verified_user(db):
    """Verified user for login/JWT flows that require is_verified=True."""
    u = User.objects.create_user(email="v@test.com", password="Pass12345/")
    u.is_verified = True
    u.save()
    return u


@pytest.fixture
def mock_email_thread_start(monkeypatch):
    """
    Prevent background email thread from running.
    We patch EmailThread.start() to a no-op so tests are deterministic.
    """
    from accounts.api.utils import EmailThread

    calls = {"count": 0}

    def _fake_start(self):
        calls["count"] += 1
        return None

    monkeypatch.setattr(EmailThread, "start", _fake_start, raising=True)
    return calls
