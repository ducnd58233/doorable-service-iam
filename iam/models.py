from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.
class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    username = models.EmailField(unique=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "user"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
