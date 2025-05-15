from django.urls import path

from . import views

urlpatterns = [
    path(
        "connected", views.ConnectedIntegrationsView.as_view(), name="integrations-list"
    ),
]
