from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django_extensions.db.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, TimeStampedModel):
    email = models.EmailField("email address", unique=True, null=False, blank=False)
    first_name = models.CharField(
        "first name", max_length=30, blank=True, db_index=True
    )
    last_name = models.CharField("last name", max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta(AbstractBaseUser.Meta):
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
