import jwt

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpRequest, HttpResponse
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

    @swagger_auto_schema(manual_parameters=[token_param_config])
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
                {"error_message": "activation expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error_message": "invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Register(APIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Create new user", request_body=serializer_class
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "error_message": "email or username already exist!",
                    "code": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
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

    @swagger_auto_schema(operation_description="Login", request_body=serializer_class)
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
