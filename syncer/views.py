from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.constants import UserIntegrationStatus
from integrations.models import UserIntegration
from syncer.services import ActivitySyncer


class IntegrationSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        source_integration_name = request.data.get("source_integration_name")
        target_integration_name = request.data.get("target_integration_name")
        source_activity_ref = request.data.get("source_activity_ref")

        source_user_integration = (
            UserIntegration.objects.filter(
                user=request.user,
                integration_name=source_integration_name,
                status=UserIntegrationStatus.COMPLETED.value,
            )
            .order_by("-created")
            .first()
        )

        target_user_integration = (
            UserIntegration.objects.filter(
                user=request.user,
                integration_name=target_integration_name,
                status=UserIntegrationStatus.COMPLETED.value,
            )
            .order_by("-created")
            .first()
        )

        syncer = ActivitySyncer(source_user_integration, target_user_integration)
        target_activity_file = syncer.sync(source_activity_ref)
        return Response(
            {"message": "Synced activity", "target_activity_file": target_activity_file}
        )
