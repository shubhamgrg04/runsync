from rest_framework import serializers

from integrations.models import UserIntegration


class UserIntegrationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserIntegration
        fields = ["id", "integration_name", "status", "created"]
