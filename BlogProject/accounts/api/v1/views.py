
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, get_object_or_404, RetrieveUpdateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializer import *
from django.core.mail import send_mail as send_mail_django_core
from mail_templated import EmailMessage
from ..utils import EmailThread
import jwt
from django.conf import settings
from accounts.services import generate_activation_token, generate_reset_password_token
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# -----------------------------
# Registration
# -----------------------------
class RegistrationApiView(GenericAPIView):
    serializer_class = RegistrationSerializer

    swagger_tags = ["Accounts / Registration"]
    swagger_summary = {"create": "Register a new user"}
    swagger_description = {
        "create": "Creates a user account, then sends an activation email containing"
                  " an activation link."
    }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_email=serializer.validated_data['email']
        user_obj=get_object_or_404(User,email=user_email)

        token=generate_activation_token(user_obj)
        activation_link = request.build_absolute_uri(
            reverse('accounts:api-v1:activation', kwargs={'token': token}))

        email_obj = EmailMessage(
            template_name= 'email/activation_email.html',
            context= {'activation_link': activation_link},
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email]
        )
        EmailThread(email_obj).start()

        return Response({'email': user_email}, status=status.HTTP_201_CREATED)


# -----------------------------
# Token Auth (DRF TokenAuth)
# -----------------------------
class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    swagger_tags = ["Auth / Token"]
    swagger_summary = {"create": "Obtain auth token"}
    swagger_description = {
        "create": "Authenticates user credentials and returns a DRF token."
    }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        profile=getattr(user,'profile',None)

        return Response({'token':token.key,
                         'user':profile.get_full_name if profile else None,
                         'email':user.email})


class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    swagger_tags = ["Auth / Token"]
    swagger_summary = {"post": "Logout (discard token)"}
    swagger_description = {"post": "Deletes the current user's DRF token."}

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# -----------------------------
# JWT Auth (SimpleJWT)
# -----------------------------
class  CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    swagger_tags = ["Auth / JWT"]
    swagger_summary = {"create": "Obtain JWT pair"}
    swagger_description = {"create": "Returns access and refresh tokens for valid user credentials."}


class JWTRefreshView(TokenRefreshView):
    """
    Wrapper for TokenRefreshView so we can apply swagger_* metadata via CustomAutoSchema.
    """
    swagger_tags = ["Auth / JWT"]
    swagger_summary = {"create": "Refresh access token"}
    swagger_description = {"create": "Takes a refresh token and returns a new access token."}


class JWTVerifyView(TokenVerifyView):
    """
    Wrapper for TokenVerifyView so we can apply swagger_* metadata via CustomAutoSchema.
    """
    swagger_tags = ["Auth / JWT"]
    swagger_summary = {"create": "Verify token"}
    swagger_description = {"create": "Verifies whether a token is valid (signature/expiration)."}


# -----------------------------
# Password Management
# -----------------------------
class ChangePasswordApiView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    swagger_tags = ["Accounts / Password"]
    swagger_summary = {"update": "Change password"}
    swagger_description = {
        "update": "Changes the current user's password after validating the old password."
    }

    def get_object(self, queryset=None):
        return self.request.user

    # @swagger_auto_schema(tags=['Password Management'])
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestApiView(GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer

    swagger_tags = ["Accounts / Password"]
    swagger_summary = {"create": "Request password reset"}
    swagger_description = {
        "create": "If the email exists, sends a password reset link to the user."
    }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        if user:
            token = generate_reset_password_token(user)
            reset_link = request.build_absolute_uri(
                reverse('accounts:api-v1:reset-password-confirm', kwargs={'token': token})
            )

            email_obj = EmailMessage(
                template_name='email/reset_password_email.html',
                context={'reset_link': reset_link},
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            EmailThread(email_obj).start()

        return Response(
            {'detail': 'If the email exists, a reset link has been sent.'},
            status=status.HTTP_200_OK
        )

class ResetPasswordConfirmApiView(GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer

    swagger_tags = ["Accounts / Password"]
    swagger_summary = {"create": "Confirm password reset"}
    swagger_description = {
        "create": "Validates reset token, then sets a new password for the user."
    }

    def post(self, request, token, *args, **kwargs):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get('type') != 'reset_password':
                raise jwt.InvalidTokenError
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['password'])
        user.save()

        return Response({'detail': 'Password reset successfully'}, status=status.HTTP_200_OK)


# -----------------------------
# Profile
# -----------------------------
class ProfileApiView(RetrieveUpdateAPIView):
    serializer_class =ProfileSerializer
    queryset = Profile.objects.all()

    swagger_tags = ["Accounts / Profile"]
    swagger_summary = {
        "retrieve": "Get current user profile",
        "update": "Update current user profile",
        "partial_update": "Partially update current user profile",
    }
    swagger_description = {
        "retrieve": "Returns the authenticated user's profile.",
        "update": "Updates the authenticated user's profile.",
        "partial_update": "Partially updates the authenticated user's profile.",
    }

    def get_object(self):
        queryset=self.get_queryset()
        return get_object_or_404(queryset,user=self.request.user)


# -----------------------------
# Activation
# -----------------------------

class ActivationApiView(APIView):
    swagger_tags = ["Accounts / Activation"]
    swagger_summary = {"get": "Activate account"}
    swagger_description = {
        "get": "Validates activation token and marks the user account as verified."
    }

    def get(self, request, token, *args, **kwargs):
        try:
            token_decoded=jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id=token_decoded.get('user_id')
        except jwt.ExpiredSignatureError:
            return Response({'details':'token has been expired'},
                            status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'details':'token is not valid'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_obj=get_object_or_404(User,id=user_id)
        if user_obj.is_verified:
            return Response({'details': 'Your account has already been verified.'})


        user_obj.is_verified=True
        user_obj.save()
        return Response({'details': 'Your account has been verified and activated successfully.'})


class ActivationResendApiView(GenericAPIView):
    serializer_class = ActivationResendSerializer

    swagger_tags = ["Accounts / Activation"]
    swagger_summary = {"create": "Resend activation email"}
    swagger_description = {
        "create": "Resends an activation email with a new activation token."
    }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_obj=serializer.validated_data['user']
        token = generate_activation_token(user_obj)

        activation_link = request.build_absolute_uri(
            reverse('accounts:api-v1:activation', kwargs={'token': token}))

        email_obj = EmailMessage(
            template_name='email/activation_email.html',
            context={'activation_link': activation_link},
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_obj.email])
        EmailThread(email_obj).start()

        return Response({'details': 'Your activation code has been resent successfully.'},
                        status=status.HTTP_200_OK)


# -----------------------------
# Debug / Test
# -----------------------------
class TestEmailSend(APIView):
    permission_classes = [IsAdminUser]

    swagger_tags = ["Accounts / Test / Debug"]
    swagger_summary = {"get": "Send activation email (test)"}
    swagger_description = {
        "get": "Admin-only debug endpoint that sends an activation email to a hardcoded address."
    }

    def get(self, request, *args, **kwargs):
        email="mohammadi.tik@gmail.com"
        user_obj = get_object_or_404(User,email=email)

        token=generate_activation_token(user_obj)
        activation_link = request.build_absolute_uri(
            reverse('accounts:api-v1:activation', kwargs={'token': token}))

        email_obj = EmailMessage(
            template_name='email/activation_email.html',
            context={'activation_link': activation_link},
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        EmailThread(email_obj).start()

        return Response(f'The activation email was sent to {email} ...')



