from django.urls import path

from . import views

urlpatterns = [
    path("fitbit", views.FitbitCallbackView.as_view(), name="fitbit-callback"),
]
