from integrations.models import UserIntegration
from integrations.services import get_integration


class ActivitySyncer:
    def __init__(
        self,
        source_user_integration: UserIntegration,
        target_user_integration: UserIntegration,
    ):
        self.source_user_integration = source_user_integration
        self.target_user_integration = target_user_integration
        self.source_integration = get_integration(
            source_user_integration.integration_name
        )(source_user_integration)
        self.target_integration = get_integration(
            target_user_integration.integration_name
        )(target_user_integration)

    def sync(self, source_activity_ref):
        (
            source_activity_file,
            source_activity_file_type,
        ) = self.source_integration.get_activity_file(source_activity_ref)
        target_activity_file = self.target_integration.upload_activity(
            source_activity_file, file_metadata={"type": source_activity_file_type}
        )
        return target_activity_file
