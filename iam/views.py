import jwt

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
)
from .models import User


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
        # responses={201: serializer_class, 400: "Bad request"},
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "error_message": "email or username already exist!",
                    "code": status.HTTP_400_BAD_REQUEST,
                },
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

        send_mail(
            subject="Verify your email",
            message=email_body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return Response(
            {"message": "Register successful!"}, status=status.HTTP_201_CREATED
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
        serializer = self.serializer_class(data=request.data)
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

        absurl = f"http://{current_site}{relative_link}"
        email_body = f"Hello. Use link below to reset your password \n {absurl}"

        send_mail(
            subject="Reset your password",
            message=email_body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
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
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {
                        "error_message": "invalid token",
                        "code": status.HTTP_401_UNAUTHORIZED,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                    exception=True,
                )

            return Response(
                {
                    "message": "valid credentials",
                    "data": {"uidb64": uidb64, "token": token},
                },
                status=status.HTTP_200_OK,
            )
        except DjangoUnicodeDecodeError:
            return Response(
                {
                    "error_message": "invalid token",
                    "code": status.HTTP_401_UNAUTHORIZED,
                },
                status=status.HTTP_401_UNAUTHORIZED,
                exception=True,
            )


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
