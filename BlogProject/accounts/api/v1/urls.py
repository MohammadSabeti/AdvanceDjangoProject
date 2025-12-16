from django.urls import path
from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

app_name = 'api-v1'
urlpatterns = [
    # registration
    path("registration/", RegistrationApiView.as_view(), name="registration"),
    # login token
    path("token/login/", CustomObtainAuthToken.as_view(), name="token-login"),
    # logout token
    path("token/logout/", CustomDiscardAuthToken.as_view(), name="token-logout"),
    # change password
    path("change-password/", ChangePasswordApiView.as_view(), name="change-password"),
    # user profile
    path("profile/", ProfileApiView.as_view(), name="profile"),

    # reset password
    # login jwt
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
]
