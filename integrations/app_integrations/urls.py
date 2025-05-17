from django.urls import path

from . import views

urlpatterns = [
    path(
        "<str:integration_name>/oauth",
        views.IntegrationOauthCallbackView.as_view(),
        name="integration-oauth-callback",
    ),
]
