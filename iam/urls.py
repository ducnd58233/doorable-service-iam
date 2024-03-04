from django.urls import path
from .views import VerifyEmail, Register

urlpatterns = [
    path("register", Register.as_view(), name="register"),
    path("email-verify", VerifyEmail.as_view(), name="email-verify"),
]
