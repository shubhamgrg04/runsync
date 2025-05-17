from integrations.app_integrations.fitbit import FitbitIntegration
from integrations.app_integrations.strava import StravaIntegration


def get_integration(integration_type):
    if integration_type == "fitbit":
        return FitbitIntegration
    elif integration_type == "strava":
        return StravaIntegration
    else:
        return None
