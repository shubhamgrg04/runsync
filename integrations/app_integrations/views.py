import structlog
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from integrations.utils import get_integration

logger = structlog.get_logger(__name__)


class IntegrationOauthCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, integration_name):
        logger.info("get_integration_oauth_callback", integration_name=integration_name)

        # TODO: Remove this once we have a better way to log the request
        request_data = {
            "request": {
                "method": request.method,
                "path": request.path,
                "headers": dict(request.headers),
                "body": request.body,
            }
        }
        logger.info("handle_oauth_callback", request=request_data)

        try:
            integration = get_integration(integration_name)
            integration.handle_oauth_callback(request)
            return redirect(settings.INTEGRATION_CALLBACK_REDIRECT_URL_SUCCESS)
        except Exception as err:
            logger.error("error_handling_oauth_callback", error=err)
            return redirect(settings.INTEGRATION_CALLBACK_REDIRECT_URL_ERROR)
