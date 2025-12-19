
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, get_object_or_404, RetrieveUpdateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from ...models import User,Profile
from .serializer import (RegistrationSerializer, CustomAuthTokenSerializer,
                         CustomTokenObtainPairSerializer, ChangePasswordSerializer, ProfileSerializer,
                         ActivationResendSerializer, ResetPasswordRequestSerializer, ResetPasswordConfirmSerializer)
from django.core.mail import send_mail as send_mail_django_core
from mail_templated import EmailMessage
from ..utils import EmailThread
import jwt
from django.conf import settings
from accounts.services import generate_activation_token, generate_reset_password_token


class RegistrationApiView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_email=serializer.validated_data['email']
        data={
            'email':user_email
        }
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
        return Response(data, status=status.HTTP_201_CREATED)

class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

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

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class  CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordApiView(GenericAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

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


class ProfileApiView(RetrieveUpdateAPIView):
    serializer_class =ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset=self.get_queryset()
        obj=get_object_or_404(queryset,user=self.request.user)
        return obj




class TestEmailSend(GenericAPIView):

    def get(self, request, *args, **kwargs):
        # only for test
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



class ActivationApiView(APIView):

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
        else:
            user_obj.is_verified=True
            user_obj.save()
            return Response({'details': 'Your account has been verified and activated successfully.'})


class ActivationResendApiView(GenericAPIView):
    serializer_class = ActivationResendSerializer

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



class ResetPasswordRequestApiView(GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer

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



