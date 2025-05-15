from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the application.
    Extends Django's AbstractUser to allow for future customization.
    """

    email = models.EmailField("email address", unique=True, null=False, blank=False)
    first_name = models.CharField(
        "first name", max_length=30, blank=True, db_index=True
    )
    last_name = models.CharField("last name", max_length=30, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
