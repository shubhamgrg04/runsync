from rest_framework import serializers

from integrations.models import UserIntegration


class UserIntegrationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserIntegration
        fields = ["id", "integration_name", "status", "created"]


class AppSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    connect_url = serializers.URLField()
    activities_url = serializers.URLField()
    status = serializers.CharField()
