from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase, APIRequestFactory

from ..models import User

class TestSetUp(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.email_verify_url = reverse("email-verify")
        self.request_pw_reset_email_url = reverse("request-reset-email")
        self.reset_pw_url = reverse("password-reset-complete")

        self.fake = Faker()

        self.user_data = {
            "email": self.fake.email(),
            "username": self.fake.user_name(),
            "password": self.fake.password(),
        }

        self.saved_user_data = {
            "email": self.fake.email(),
            "username": self.fake.user_name(),
            "password": self.fake.password(),
        }

        self.saved_user = User.objects.create(**self.saved_user_data)

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
