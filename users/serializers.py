from django.contrib.auth import authenticate
from rest_framework import serializers

from users.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(
        required=True, min_length=12, max_length=128, write_only=True
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")

        return data


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, min_length=3, max_length=30)
    last_name = serializers.CharField(required=True, min_length=3, max_length=30)
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(
        required=True, min_length=12, max_length=128, write_only=True
    )

    class Meta:
        model = User
        fields = ("password", "first_name", "last_name", "email")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
