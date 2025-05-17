import logging

from django.conf import settings
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from integrations.utils import get_integration

logger = logging.getLogger(__name__)


class IntegrationOauthCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, integration_name):
        try:
            integration = get_integration(integration_name)
            integration.handle_oauth_callback(request)
            return redirect(settings.INTEGRATION_CALLBACK_REDIRECT_URL_SUCCESS)
        except Exception as err:
            logger.error(f"Error handling {integration_name} callback: {err}")
            return redirect(settings.INTEGRATION_CALLBACK_REDIRECT_URL_ERROR)
