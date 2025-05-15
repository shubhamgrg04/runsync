from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"message": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"message": "Account is disabled"}, status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT token with user ID and expiry
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

        # Set token in both response and httponly cookie
        response = Response(
            {"token": token, "user": {"id": user.id, "username": user.username}},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=86400,  # 1 day in seconds
        )

        return response


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        User.objects.create_user(username=username, password=password)
        return Response(
            {"message": "User registered successfully"}, status=status.HTTP_201_CREATED
        )


class GoogleOAuthView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"message": "Missing code"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "Hello, world!"})
