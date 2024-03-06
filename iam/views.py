import jwt
import logging

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.encoding import (
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    LogoutSerializer,
)
from .models import User
from .tasks import send_email
from .utils import CustomRedirect

logger = logging.getLogger(__name__)


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Access Token from email",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        manual_parameters=[token_param_config],
        responses={200: "email successfully activated!", 400: "Bad request"},
    )
    def get(self, request: HttpRequest) -> HttpResponse:
        token = request.GET.get("token")

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM
            )
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response(
                {"message": "email successfully activated!"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {
                    "error_message": "activation expired",
                    "code": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=True,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {
                    "error_message": "invalid token",
                    "code": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=True,
            )


class Register(APIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Create new user",
        request_body=serializer_class,
        responses={201: serializer_class, 400: "Bad request"},
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
                exception=True,
            )
        serializer.save()

        user = User.objects.get(email=request.data["email"])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relative_link = reverse("email-verify")

        absurl = f"http://{current_site}{relative_link}?token={str(token)}"
        email_body = (
            f"Hi {user.username}. Use link below to verify your email \n {absurl}"
        )

        message = {
            "subject": "Verify your email",
            "username": user.username,
            "message": email_body,
            "recipient_list": [user.email],
        }

        send_email.delay(message)

        return Response(
            {"message": "register successful!"}, status=status.HTTP_201_CREATED
        )


class Login(APIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="Login",
        request_body=serializer_class,
        responses={200: serializer_class, 400: "Bad request"},
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(APIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    @swagger_auto_schema(
        operation_description="Request to reset the password",
        request_body=serializer_class,
        responses={200: serializer_class, 404: "User not found"},
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        self.serializer_class(data=request.data)
        email = request.data["email"]

        users = User.objects.filter(email=email)
        if not users.exists():
            return Response(
                {"error_message": "user not found", "code": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
                exception=True,
            )

        user = users.first()
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        current_site = get_current_site(request).domain
        relative_link = reverse(
            "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
        )

        redirect_url = request.data.get("redirect_url", "")
        absurl = f"http://{current_site}{relative_link}?redirect_url={redirect_url}"
        email_body = f"Use link below to reset your password \n {absurl}"

        message = {
            "subject": "Reset your password",
            "message": email_body,
            "recipient_list": [user.email],
        }

        send_email.delay(message)
        return Response(
            {"message": "link to reset password have been sent"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheck(APIView):

    @swagger_auto_schema(
        operation_description="Check the reset password token",
        responses={401: "invalid token"},
    )
    def get(self, request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
        redirect_url = request.GET.get("redirect_url")

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if redirect_url and len(redirect_url) > 3:
                    return CustomRedirect(f"{redirect_url}?token_valid=False")
                return CustomRedirect(f"{settings.FRONTEND_URL}?token_valid=False")

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    f"{redirect_url}?token_valid=True&message=valid credentials&uidb64={uidb64}&token={token}"
                )
            return CustomRedirect(f"{settings.FRONTEND_URL}?token_valid=True")

        except DjangoUnicodeDecodeError:
            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(f"{redirect_url}?token_valid=False")
            return CustomRedirect(f"{settings.FRONTEND_URL}?token_valid=False")


class SetNewPassword(APIView):
    serializer_class = SetNewPasswordSerializer

    @swagger_auto_schema(
        operation_description="Check the reset password token",
        request_body=serializer_class,
        responses={401: "Unauthorized"},
    )
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password reset successful!"}, status=status.HTTP_200_OK
        )


class Logout(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Logout",
        request_body=serializer_class,
        responses={200: None},
    )
    def post(self, request: HttpRequest):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfile(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: HttpRequest, id: int) -> HttpResponse:
        token = request.auth
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
        user = User.objects.get(id=payload["user_id"])

        if id != user.id:
            return Response(data={})
        return Response(data=user)

    def patch(self, request: HttpRequest) -> HttpResponse:
        return Response
