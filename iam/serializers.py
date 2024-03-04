from typing import Dict

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: Dict):
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
