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


class StravaIntegration(BaseIntegration):
    INTEGRATION_NAME = IntegrationName.STRAVA
    TOKEN_URL = "https://www.strava.com/oauth/token"
    AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"

    CLIENT_ID = settings.STRAVA_CLIENT_ID
    CLIENT_SECRET = settings.STRAVA_CLIENT_SECRET

    """
    Strava API Reference:
    https://developers.strava.com/docs/authentication/
    https://developers.strava.com/docs/reference/
    """

    def __init__(self, user_integration):
        super().__init__(user_integration)

    @classmethod
    def handle_oauth_callback(cls, request):
        super().handle_oauth_callback(request)
        code = request.GET.get("code")
        if not code:
            raise ValueError("No code provided")
        state = request.GET.get("state")
        if not state:
            raise ValueError("No state provided")
        user_integration = (
            UserIntegration.objects.filter(
                integration_name=cls.INTEGRATION_NAME.value, state=state
            )
            .order_by("-created")
            .first()
        )
        if not user_integration:
            raise ValueError("No user integration found")
        res = cls.exchange_code_for_token(code)
        access_token, refresh_token, expires_in, _ = (
            res.pop("access_token"),
            res.pop("refresh_token"),
            res.pop("expires_in"),
            res.pop("expires_at"),
        )
        user_integration.access_token = access_token
        user_integration.refresh_token = refresh_token
        user_integration.expires_at = timezone.now() + timedelta(seconds=expires_in)
        user_integration.status = UserIntegrationStatus.COMPLETED.value
        user_integration.metadata = res
        user_integration.save(
            update_fields=[
                "access_token",
                "refresh_token",
                "expires_at",
                "status",
                "metadata",
            ]
        )

    @classmethod
    def exchange_code_for_token(cls, code):
        data = {
            "client_id": cls.CLIENT_ID,
            "client_secret": cls.CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        }
        res = requests.post(cls.TOKEN_URL, params=data)
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
            "response_type": "code",
            "redirect_uri": settings.STRAVA_REDIRECT_URI,
            "approval_prompt": "auto",
            "scope": "read,activity:read_all,activity:write",
            "state": random_state,
        }
        return f"{cls.AUTHORIZE_URL}?{urlencode(params)}"

    def fetch_activities(self, since=None):
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        since = since or timezone.now() - timedelta(days=25)
        params = {
            "after": int(since.timestamp()),
            "per_page": 30,
        }
        url = "https://www.strava.com/api/v3/athlete/activities"
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        return self.filter_activities(res.json())

    def filter_activities(self, activities):
        return [activity for activity in activities if activity.get("distance", 0) > 0]

    def get_activity_details(self, activity_id):
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json()

    def get_activity_file(self, activity_id):
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Accept": "application/gpx+xml",
        }
        url = f"https://www.strava.com/api/v3/activities/{activity_id}/export_tcx"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.text, res.headers.get("Content-Type")

    def upload_activity(
        self, activity_file, file_metadata=None, activity_metadata=None
    ):
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        url = "https://www.strava.com/api/v3/uploads"
        files = {
            "file": (
                "activity.tcx",
                activity_file.encode("utf-8")
                if isinstance(activity_file, str)
                else activity_file,
                "application/xml",
            )
        }
        data = {
            "data_type": "tcx",
        }
        res = requests.post(url, headers=headers, files=files, data=data)
        res.raise_for_status()
        return res.json()

    def push_activity(self, user, activity_data):
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}
        url = "https://www.strava.com/api/v3/activities"
        data = {
            "name": activity_data.get("name", "Synced Activity"),
            "type": activity_data.get("type", "Run"),
            "start_date_local": activity_data["start_date_local"],
            "elapsed_time": activity_data["elapsed_time"],  # seconds
            "description": activity_data.get("description", ""),
            "distance": activity_data.get("distance", 0),  # meters
        }
        res = requests.post(url, headers=headers, data=data)
        res.raise_for_status()
        return res.json()
