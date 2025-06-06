from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.constants import IntegrationName, UserIntegrationStatus
from integrations.models import UserIntegration
from integrations.serializers import AppSerializer, UserIntegrationListSerializer
from integrations.services import get_integration


class AppsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppSerializer

    def get(self, request):
        all_apps = IntegrationName.choices()
        connected_apps = (
            UserIntegration.objects.filter(
                user=request.user, status=UserIntegrationStatus.COMPLETED.value
            )
            .order_by("integration_name", "-created")
            .distinct("integration_name")
            .values_list("integration_name", flat=True)
        )

        response = []
        for app in all_apps:
            app_data = {
                "name": app[1],
                "type": app[0],
                "connect_url": reverse(
                    "integration-oauth", kwargs={"integration_type": app[0]}
                ),
                "activities_url": reverse(
                    "integration-activity", kwargs={"integration_type": app[0]}
                ),
                "status": "connected" if app[0] in connected_apps else "not_connected",
                # "status": "not_connected" if app[0] in connected_apps else "connected",
            }
            response.append(app_data)

        response = self.serializer_class(response, many=True)
        return Response(response.data)


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
        return Response({"redirect_url": integration_url})


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
