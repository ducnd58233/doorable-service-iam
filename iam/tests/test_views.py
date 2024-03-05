from django.urls import reverse
import jwt
from datetime import datetime, timedelta

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings

from django.utils.encoding import (
    smart_bytes,
)
from django.utils.http import urlsafe_base64_encode

from rest_framework import status

from .test_setup import TestSetUp
from ..models import User


class TestRegisterViews(TestSetUp):
    def test_user_cannot_register_with_no_data(self):
        res = self.client.post(path=self.register_url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_register_correctly(self):
        res = self.client.post(
            path=self.register_url, data=self.user_data, format="json"
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["message"], "register successful!")


class TestLoginViews(TestSetUp):
    def test_user_cannot_login_with_unverified_email(self):
        self.client.post(path=self.register_url, data=self.user_data, format="json")
        res = self.client.post(path=self.login_url, data=self.user_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_login_after_verification(self):
        self.client.post(path=self.register_url, data=self.user_data, format="json")
        user = User.objects.get(email=self.user_data["email"])
        user.is_verified = True
        user.save()

        res = self.client.post(
            path=self.login_url,
            data=self.user_data,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestVerifyEmailViews(TestSetUp):
    def test_user_cannot_verify_with_invalid_token(self):
        payload = {"user_id": self.saved_user.id}
        invalid_token = jwt.encode(
            payload=payload, key="", algorithm=settings.JWT_ALGORITHM
        )

        url = f"{self.email_verify_url}?token={invalid_token}"
        res = self.client.get(path=url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["error_message"], "invalid token")

    def test_user_cannot_verify_with_expired_token(self):
        payload = {
            "user_id": self.saved_user.id,
            "exp": datetime.utcnow() - timedelta(days=10),
        }
        expired_token = jwt.encode(
            payload=payload,
            key=settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        url = f"{self.email_verify_url}?token={expired_token}"
        res = self.client.get(path=url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["error_message"], "activation expired")

    def test_user_can_verify_with_valid_token(self):
        payload = {
            "user_id": self.saved_user.id,
        }
        token = jwt.encode(
            payload=payload,
            key=settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        url = f"{self.email_verify_url}?token={token}"
        res = self.client.get(path=url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestRequestPasswordResetEmailViews(TestSetUp):
    def test_user_cannot_send_request_with_email_not_exists(self):
        res = self.client.post(
            path=self.request_pw_reset_email_url,
            data={"email": self.user_data["email"]},
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_send_request_with_valid_email(self):
        res = self.client.post(
            path=self.request_pw_reset_email_url,
            data={"email": self.saved_user_data["email"]},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestPasswordTokenCheck(TestSetUp):
    def test_user_cannot_confirm_with_invalid_link(self):
        current_site = "localhost:80"
        relative_link = reverse(
            "password-reset-confirm", kwargs={"uidb64": "MZ", "token": "123"}
        )
        invalid_link = f"http://{current_site}{relative_link}"

        res = self.client.get(path=invalid_link)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_confirm_with_valid_link(self):
        user = User.objects.get(email=self.saved_user_data["email"])

        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        current_site = "localhost:80"
        relative_link = reverse(
            "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        valid_link = f"http://{current_site}{relative_link}"

        res = self.client.get(path=valid_link)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestSetNewPassword(TestSetUp):
    def test_user_cannot_reset_password_with_invalid_params(self):
        res = self.client.patch(
            path=self.reset_pw_url,
            data={"password": "new_password", "token": "invalid_token", "uidb64": "MA"},
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_reset_password_with_valid_params(self):
        user = User.objects.get(email=self.saved_user_data["email"])

        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        res = self.client.patch(
            path=self.reset_pw_url,
            data={"password": "new_password", "token": token, "uidb64": uidb64},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
