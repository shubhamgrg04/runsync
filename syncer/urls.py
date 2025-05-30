from django.urls import path

from . import views

urlpatterns = [
    path(
        "sync",
        views.IntegrationSyncView.as_view(),
        name="integration-sync",
    ),
]
