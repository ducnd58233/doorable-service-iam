from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class Register(APIView):
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "message": "email or username already exist!",
                    "code": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()

        return Response(
            {"message": "Register successful!"}, status=status.HTTP_201_CREATED
        )
