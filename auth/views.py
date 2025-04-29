import jwt
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # generate a jwt token
        token = jwt.encode({"username": username}, "secret", algorithm="HS256")

        # set the token in the response headers and cookies
        response = Response({"token": token}, status=status.HTTP_200_OK)
        response.set_cookie(
            key="token", value=token, httponly=True, secure=True, samesite="strict"
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
