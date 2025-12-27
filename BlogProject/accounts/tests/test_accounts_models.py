import pytest

from accounts.models import Profile, User


@pytest.mark.django_db
class TestUserManager:
    """Unit tests for the custom UserManager."""

    def test_create_user_requires_email(self):
        """create_user should raise ValueError if email is missing."""
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="Pass12345/")

    def test_create_user_normalizes_email(self):
        """create_user should normalize the email casing/domain."""
        user = User.objects.create_user(email="TEST@Example.com", password="Pass12345/")
        assert user.email == "TEST@example.com"

    def test_create_superuser_sets_required_flags(self):
        """create_superuser should set is_staff/is_superuser/is_active/is_verified = True."""
        admin = User.objects.create_superuser(
            email="admin@test.com", password="Pass12345/"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True
        assert admin.is_verified is True

    def test_create_superuser_requires_is_staff_true(self):
        """create_superuser must enforce is_staff=True."""
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="admin2@test.com",
                password="Pass12345/",
                is_staff=False,
            )

    def test_create_superuser_requires_is_superuser_true(self):
        """create_superuser must enforce is_superuser=True."""
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="admin3@test.com",
                password="Pass12345/",
                is_superuser=False,
            )


@pytest.mark.django_db
class TestProfileModel:
    """Unit tests for Profile model behavior."""

    def test_profile_full_name_property(self):
        """get_full_name should return 'first last'."""
        user = User.objects.create_user(email="u@test.com", password="Pass12345/")
        # Assumes Profile is created via signals. If not, create explicitly.
        profile = getattr(user, "profile", None) or Profile.objects.create(
            user=user, first_name="John", last_name="Doe", description="x"
        )
        profile.first_name = "John"
        profile.last_name = "Doe"
        profile.description = "desc"
        profile.save()

        assert profile.get_full_name == "John Doe"
        assert str(profile).endswith(user.email)
