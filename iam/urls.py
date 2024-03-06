from django.urls import path
from .views import (
    VerifyEmail,
    Register,
    Login,
    Logout,
    PasswordTokenCheck,
    RequestPasswordResetEmail,
    SetNewPassword,
    UserProfile,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("profile", UserProfile.as_view(), name="profile"),
    path("register", Register.as_view(), name="register"),
    path("login", Login.as_view(), name="login"),
    path("logout", Logout.as_view(), name="logout"),
    path("email-verify", VerifyEmail.as_view(), name="email-verify"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path(
        "request-reset-email",
        RequestPasswordResetEmail.as_view(),
        name="request-reset-email",
    ),
    path(
        "password-reset/<uidb64>/<token>",
        PasswordTokenCheck.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete",
        SetNewPassword.as_view(),
        name="password-reset-complete",
    ),
]
