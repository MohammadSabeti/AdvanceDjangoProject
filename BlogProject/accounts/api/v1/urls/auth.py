from django.urls import path
from ..views import *

urlpatterns = [
    # registration
    path("registration/", RegistrationApiView.as_view(), name="registration"),

    path("test-email/", TestEmailSend.as_view(), name="test-email"),
    # activation
    path("activation/confirm/<str:token>/", ActivationApiView.as_view(), name="activation"),
    # resend activation
    path("activation/resend/", ActivationResendApiView.as_view(), name="activation-resend"),

    # login token
    path("login/", CustomObtainAuthToken.as_view(), name="token-login"),
    # logout token
    path("logout/", CustomDiscardAuthToken.as_view(), name="token-logout"),
    # change password
    path("change-password/", ChangePasswordApiView.as_view(), name="change-password"),

    # reset password
    path("reset-password/",ResetPasswordRequestApiView.as_view(),name="reset-password"),
    path("reset-password/confirm/<str:token>/",ResetPasswordConfirmApiView.as_view(),
         name="reset-password-confirm"),

    # login jwt
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', JWTRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', JWTVerifyView.as_view(), name='jwt-verify'),
]
