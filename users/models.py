from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the application.
    Extends Django's AbstractUser to allow for future customization.
    """

    email = models.EmailField(unique=True)

    # Add any additional fields here

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
