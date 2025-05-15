from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.constants import UserIntegrationStatus
from integrations.models import UserIntegration
from integrations.serializers import UserIntegrationListSerializer
from integrations.utils import get_integration


class ConnectedIntegrationsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserIntegrationListSerializer

    def get(self, request):
        integrations = UserIntegration.objects.filter(
            user=request.user, status=UserIntegrationStatus.COMPLETED.value
        ).order_by("-created")
        serializer = self.serializer_class(integrations, many=True)
        return Response(serializer.data)


class IntegrationOAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, integration_type):
        # get integration based on integration_type
        integration = get_integration(integration_type)
        if not integration:
            return Response({"error": "Invalid integration type"}, status=400)
        integration_url = integration.get_authorization_url(request.user)
        return Response({"integration_url": integration_url})


class IntegrationActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, integration_type):
        integration = get_integration(integration_type)
        if not integration:
            return Response({"error": "Invalid integration type"}, status=400)

        user_integration = (
            UserIntegration.objects.filter(
                user=request.user,
                integration_name=integration_type,
                status=UserIntegrationStatus.COMPLETED.value,
            )
            .order_by("-created")
            .first()
        )
        if not user_integration:
            return Response({"error": "User integration not found"}, status=400)

        activities = integration(user_integration).fetch_activities()
        return Response({"activities": activities})
