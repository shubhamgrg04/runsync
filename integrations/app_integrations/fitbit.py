import base64
import hashlib
import uuid
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone

from integrations.app_integrations import BaseIntegration
from integrations.constants import IntegrationName, UserIntegrationStatus
from integrations.models import UserIntegration
from users.models import User


class FitbitIntegration(BaseIntegration):
    INTEGRATION_NAME = IntegrationName.FITBIT
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    AUTHORIZE_URL = "https://www.fitbit.com/oauth2/authorize"

    CLIENT_ID = settings.FITBIT_CLIENT_ID
    CLIENT_SECRET = settings.FITBIT_CLIENT_SECRET

    """
    Fitbit API Reference:
    https://dev.fitbit.com/build/reference/web-api/developer-guide/authorization/
    """

    def __init__(self, user_integration):
        super().__init__(user_integration)

    @classmethod
    def handle_oauth_callback(self, request):
        super().handle_oauth_callback(request)
        code = request.GET.get("code")
        if not code:
            raise ValueError("No code provided")
        state = request.GET.get("state")
        if not state:
            raise ValueError("No state provided")
        user_integration = (
            UserIntegration.objects.filter(
                integration_name=self.INTEGRATION_NAME.value, state=state
            )
            .order_by("-created")
            .first()
        )
        if not user_integration:
            raise ValueError("No user integration found")
        res = self.exchange_code_for_token(code, code_verifier=state)
        access_token, refresh_token, expires_in = (
            res.get("access_token"),
            res.get("refresh_token"),
            res.get("expires_in"),
        )
        user_integration.access_token = access_token
        user_integration.refresh_token = refresh_token
        user_integration.expires_at = timezone.now() + timedelta(seconds=expires_in)
        user_integration.status = UserIntegrationStatus.COMPLETED.value
        user_integration.save(
            update_fields=["access_token", "refresh_token", "expires_at", "status"]
        )

    @classmethod
    def exchange_code_for_token(cls, code, *args, **kwargs):
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
            "code_verifier": kwargs.get("code_verifier"),
        }
        res = requests.post(cls.TOKEN_URL, data=data, headers=headers)
        res.raise_for_status()
        return res.json()

    @classmethod
    def get_authorization_url(cls, user: User):
        random_state = (
            base64.urlsafe_b64encode(
                hashlib.sha256(str(uuid.uuid4()).encode()).digest()
            )
            .decode("utf-8")[:96]
            .rstrip("=")
        )
        UserIntegration.objects.create(
            user=user,
            integration_name=cls.INTEGRATION_NAME.value,
            state=random_state,
        )
        params = {
            "client_id": cls.CLIENT_ID,
            "scope": "activity profile",
            "response_type": "code",
            "code_challenge": base64.urlsafe_b64encode(
                hashlib.sha256(random_state.encode()).digest()
            )
            .decode("utf-8")
            .rstrip("="),
            "code_challenge_method": "S256",
            "state": random_state,
        }
        return f"{cls.AUTHORIZE_URL}?{urlencode(params)}"

    def fetch_activities(self, since=None):
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        url = "https://api.fitbit.com/1/user/-/activities/list.json"
        since = since or timezone.now() - timedelta(days=30)
        params = {
            "afterDate": since.strftime("%Y-%m-%d") if since else "2024-01-01",
            "sort": "desc",
            "offset": 0,
            "limit": 20,
        }
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        return res.json().get("activities", [])

    def push_activity(self, user, activity_data):
        # Fitbit doesn't support pushing activities externally
        raise NotImplementedError("Pushing activities to Fitbit is not supported.")

    def handle_webhook(self, data):
        # Fitbit sends user_id, collectionType (e.g., activities), date
        print("Webhook received from Fitbit:", data)
        # you can enqueue a sync task here
