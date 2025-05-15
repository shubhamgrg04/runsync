from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        try:
            # Extract the token from the header
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != "bearer":
                return None
            token = auth_parts[1]

            # Decode and verify the token
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise AuthenticationFailed(_("Token has expired"))

            # Get the user
            user_id = payload.get("user_id")
            if not user_id:
                raise AuthenticationFailed(_("Invalid token payload"))

            user = User.objects.get(id=user_id)
            if not user.is_active:
                raise AuthenticationFailed(_("User is inactive"))

            return (user, None)

        except jwt.InvalidTokenError:
            raise AuthenticationFailed(_("Invalid token"))
        except User.DoesNotExist:
            raise AuthenticationFailed(_("User not found"))
        except Exception as e:
            raise AuthenticationFailed(str(e))

    def authenticate_header(self, request):
        return "Bearer"
