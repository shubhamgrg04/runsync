from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "connected", views.ConnectedIntegrationsView.as_view(), name="integrations-list"
    ),
    path(
        "<str:integration_type>/connect",
        views.IntegrationOAuthView.as_view(),
        name="integration-oauth",
    ),
    path(
        "<str:integration_type>/activities",
        views.IntegrationActivityView.as_view(),
        name="integration-activity",
    ),
    # callback urls
    path("callback/", include("integrations.app_integrations.urls")),
]
