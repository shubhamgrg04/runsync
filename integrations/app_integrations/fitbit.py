import base64
import hashlib
import uuid
from datetime import timedelta
from urllib.parse import urlencode

import requests
import structlog
from django.conf import settings
from django.utils import timezone

from integrations.app_integrations import BaseIntegration
from integrations.constants import IntegrationName, UserIntegrationStatus
from integrations.models import UserIntegration
from users.models import User

logger = structlog.get_logger(__name__)


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
                integration_name=self.INTEGRATION_NAME.value,
                state=state,
                status=UserIntegrationStatus.PENDING.value,
            )
            .order_by("-created")
            .first()
        )
        if not user_integration:
            raise ValueError("No user integration found")

        try:
            res = self.exchange_code_for_token(code, code_verifier=state)
            access_token, refresh_token, expires_in = (
                res.pop("access_token"),
                res.pop("refresh_token"),
                res.pop("expires_in"),
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
        except Exception as e:
            logger.error("error_exchanging_code_for_token", error=e)
            user_integration.status = UserIntegrationStatus.FAILED.value
            user_integration.metadata = {"error": str(e)}
            user_integration.save(update_fields=["status", "metadata"])
            raise e

    @classmethod
    def exchange_code_for_token(cls, code, *args, **kwargs):
        try:
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
        except Exception as e:
            logger.error("error_exchanging_code_for_token", error=e)
            raise e

    @classmethod
    def get_authorization_url(cls, user: User):
        try:
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
                "scope": "activity profile heartrate location electrocardiogram nutrition oxygen_saturation temperature weight",
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
        except Exception as e:
            logger.error("error_getting_authorization_url", error=e)
            raise e

    def fetch_activities(self, since=None):
        try:
            headers = {"Authorization": f"Bearer {self.get_access_token()}"}
            url = "https://api.fitbit.com/1/user/-/activities/list.json"
            since = since or timezone.now() - timedelta(days=7)
            params = {
                "afterDate": since.strftime("%Y-%m-%d"),
                "sort": "desc",
                "offset": 0,
                "limit": 20,
            }
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            return self.filter_activities(res.json().get("activities", []))
        except Exception as e:
            logger.error("error_fetching_activities", error=e)
            raise e

    def filter_activities(self, activities):
        try:
            return [
                activity
                for activity in activities
                if isinstance(activity.get("distance"), float)
                and activity.get("distance") > 0
            ]
        except Exception as e:
            logger.error("error_filtering_activities", error=e)
            raise e

    def get_activity_details(self, log_id):
        try:
            headers = {"Authorization": f"Bearer {self.get_access_token()}"}
            url = f"https://api.fitbit.com/1/user/-/activities/{log_id}.json"
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error("error_getting_activity_details", error=e)
            raise e

    def get_activity_file(self, log_id):
        try:
            headers = {"Authorization": f"Bearer {self.get_access_token()}"}
            user_id = self.user_integration.metadata.get("user_id")
            url = f"https://api.fitbit.com/1/user/{user_id}/activities/{log_id}.tcx"
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return res.text, res.headers.get("Content-Type")
        except Exception as e:
            logger.error("error_getting_activity_file", error=e)
            raise e

    def upload_activity(
        self, activity_file, file_metadata=None, activity_metadata=None
    ):
        try:
            headers = {"Authorization": f"Bearer {self.get_access_token()}"}
            url = "https://api.fitbit.com/1/user/-/activities"
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
        except Exception as e:
            logger.error("error_uploading_activity", error=e)
            raise e
