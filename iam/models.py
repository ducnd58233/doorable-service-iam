from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


# Create your models here.
class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "user"
