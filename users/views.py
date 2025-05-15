from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import LoginSerializer, RegisterSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"message": "Account is disabled"}, status=status.HTTP_403_FORBIDDEN
            )

        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": timezone.now() + timedelta(days=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        response = Response(
            {"token": token, "user": {"id": user.id, "email": user.email}},
            status=status.HTTP_200_OK,
        )
        return response


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"message": "User registered successfully"}, status=status.HTTP_201_CREATED
        )
