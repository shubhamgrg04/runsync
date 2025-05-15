import logging

from django.conf import settings
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .fitbit import FitbitIntegration

logger = logging.getLogger(__name__)


class FitbitCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            FitbitIntegration.handle_oauth_callback(request)
            return redirect(settings.INTEGRATION_CALLBACK_REDIRECT_URL_SUCCESS)
        except Exception as err:
            logger.error(f"Error handling fitbit callback: {err}")
            return redirect(settings.INTEGRATION_CALLBACK_REDIRECT_URL_ERROR)
