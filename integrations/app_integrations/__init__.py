import base64
import uuid
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.utils import timezone

from integrations.models import UserIntegration
from users.models import User


class BaseIntegration:
    def __init__(self, user_integration):
        self.user_integration = user_integration

    @classmethod
    def handle_oauth_callback(cls, request):
        pass

    @classmethod
    def exchange_code_for_token(cls, code):
        basic_auth = base64.b64encode(
            f"{cls.CLIENT_ID}:{cls.CLIENT_SECRET}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": cls.CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
        }
        res = requests.post(cls.TOKEN_URL, data=data, headers=headers)
        res.raise_for_status()
        return res.json()

    @classmethod
    def exchange_refresh_token_for_token(cls, refresh_token):
        basic_auth = base64.b64encode(
            f"{cls.CLIENT_ID}:{cls.CLIENT_SECRET}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": cls.CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        res = requests.post(cls.TOKEN_URL, data=data, headers=headers)
        res.raise_for_status()
        return res.json()

    @classmethod
    def get_authorization_url(cls, user: User):
        random_state = str(uuid.uuid4())
        UserIntegration.objects.create(
            user=user, integration_name=cls.INTEGRATION_NAME.value, state=random_state
        )
        params = {
            "client_id": cls.CLIENT_ID,
            "scope": "activity profile",
            "response_type": "code",
            "state": random_state,
        }
        return f"{cls.AUTHORIZE_URL}?{urlencode(params)}"

    def get_access_token(self):
        if self.user_integration.is_token_expired:
            res = self.exchange_refresh_token_for_token(
                self.user_integration.refresh_token
            )
            access_token, refresh_token, expires_in = (
                res.get("access_token"),
                res.get("refresh_token"),
                res.get("expires_in"),
            )
            self.user_integration.access_token = access_token
            self.user_integration.refresh_token = refresh_token
            self.user_integration.expires_at = timezone.now() + timedelta(
                seconds=expires_in
            )
            self.user_integration.save(
                update_fields=["access_token", "refresh_token", "expires_at"]
            )
        return self.user_integration.access_token
