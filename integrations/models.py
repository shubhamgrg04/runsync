from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel

from integrations.constants import IntegrationName, UserIntegrationStatus
from users.models import User


class UserIntegration(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    integration_name = models.CharField(
        max_length=255, choices=IntegrationName.choices(), db_index=True
    )
    status = models.CharField(
        max_length=255,
        choices=UserIntegrationStatus.choices(),
        default=UserIntegrationStatus.PENDING.value,
        db_index=True,
    )
    state = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    access_token = models.CharField(max_length=2048, null=True, blank=True)
    refresh_token = models.CharField(max_length=2048, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    metadata = JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username} - {self.integration_name}"

    @property
    def is_token_expired(self):
        return self.expires_at and self.expires_at < timezone.now()
