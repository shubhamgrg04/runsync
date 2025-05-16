"""
Local Django settings
"""
import os

from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-n)n+svh=oi=$ldx7ls^er%jxkw#0hu4q1$mdt(hw5rr16!8sic"
JWT_SECRET_KEY = "django-insecure-n)n+svh=oi=$ldx7ls^er%jxkw#0hu4q1$mdt(hw5rr16!8sic"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "runsync",
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
