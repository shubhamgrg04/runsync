from integrations.app_integrations.fitbit import FitbitIntegration


def get_integration(integration_type):
    if integration_type == "fitbit":
        return FitbitIntegration
    else:
        return None
