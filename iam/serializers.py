from typing import Dict

from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=128)

    class Meta(object):
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: Dict) -> User:
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ["token"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=3, max_length=255)
    password = serializers.CharField(min_length=6, max_length=128, write_only=True)
    username = serializers.CharField(min_length=3, max_length=255, read_only=True)
    tokens = serializers.DictField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "username", "tokens"]

    def validate(self, attrs: Dict) -> Dict:
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("account disabled, contact admin")

        if not user.is_verified:
            raise AuthenticationFailed("email is not verified")

        return {
            "email": user.email,
            "username": user.username,
            "tokens": user.tokens,
        }


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=3, max_length=255)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=128, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        model = User
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs: Dict) -> Dict:
        try:
            password = attrs.get("password", "")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("the reset link is invalid", status.HTTP_401_UNAUTHORIZED)

            user.set_password(password)
            user.save()
        except Exception:
            raise AuthenticationFailed(
                "the reset link is invalid", status.HTTP_401_UNAUTHORIZED
            )
        return super().validate(attrs)
