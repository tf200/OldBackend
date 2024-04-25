"""
Django settings for healty project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv
from loguru import logger

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# Configuring the logs
logger.add(
    BASE_DIR / "logs/file.log",
    rotation="100 MB",
    retention="30 days",
    enqueue=True,
    backtrace=True,
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-vrw!mq7f#wac=db+jgzumdn-slvi@ce7*@-!ks3!6)1*#dx!&="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DEBUG", 0)))

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "rest_framework",
    "django_filters",
    "django_extensions",
    "storages",
    "corsheaders",
    "django_celery_results",
    "system",
    "assessments",
    "ai",
    "authentication",
    "client",
    "employees",
    "adminmodif",
    "planning",
    "channels",
    "chat",
]


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}
SIMPLE_JWT = {
    # It will work instead of the default serializer(TokenObtainPairSerializer).
    "TOKEN_OBTAIN_SERIALIZER": "authentication.serializers.MyTokenObtainPairSerializer",
    "ACCESS_TOKEN_LIFETIME": timedelta(days=90),  # Set access token lifetime to 5 minutes
    "REFRESH_TOKEN_LIFETIME": timedelta(days=95),
    # ...
}
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "healty.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# WSGI_APPLICATION = 'healty.wsgi.application'
ASGI_APPLICATION = "healty.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", ""),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASS", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

USE_S3: bool = bool(int(os.getenv("DEBUG", 0)))

if USE_S3:
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME: str = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
    AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL", None)
    AWS_S3_REGION_NAME: str = os.getenv("AWS_S3_REGION_NAME", "us-east-2")  # e.g., us-east-2
    AWS_S3_CUSTOM_DOMAIN: str = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # Media files
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")


AUTH_USER_MODEL = "authentication.CustomUser"
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
CORS_ALLOW_ALL_ORIGINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django Ninja
NINJA_PAGINATION_PER_PAGE = 30

REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")
ACCEPT_CONTENT = ["application/json"]
RESULT_BACKEND = "django-db"
CELERY_RESULT_BACKEND = "django-db"
TASK_SERIALIZER = "json"
RESULT_SERIALIZER = "json"
broker_connection_retry_on_startup = True
broker_connection_retry = True
CELERY_TASK_TIME_LIMIT = 900
CELERY_TASK_SOFT_TIME_LIMIT = 850

MEDICATION_RECORDS_CREATATION: int = 60  # in minutes

CELERY_BEAT_SCHEDULE = {
    "clear_temporary_files_daily": {
        "task": "planning.tasks.clear_temporary_files",
        "schedule": crontab(minute="0", hour="0"),  # Runs daily at midnight
    },
    "summarize_weekly_reports": {
        "task": "employees.tasks.summarize_weekly_reports",
        "schedule": crontab(minute="0", hour="0", day_of_week="6"),
    },
    "invoice_creation_per_month": {
        "task": "client.tasks.invoice_creation_per_month",
        "schedule": crontab(minute="0", hour="0", day_of_month="28"),
    },
    "invoice_mark_as_expired": {
        "task": "client.tasks.invoice_mark_as_expired",
        "schedule": crontab(minute="0", hour="*/1"),  # Runs per hour
    },
    "invoice_send_notification_3_months_before": {
        "task": "client.tasks.invoice_send_notification_3_months_before",
        "schedule": crontab(minute="0", hour="*/1"),  # Runs per hour
    },
    "create_and_send_medication_record_notification": {
        "task": "client.tasks.create_and_send_medication_record_notification",
        "schedule": crontab(
            minute=f"*/{MEDICATION_RECORDS_CREATATION}",
        ),  # every hour
    },
    "send_contract_reminders": {
        "task": "client.tasks.send_contract_reminders",
        "schedule": crontab(minute="0", hour="0", day_of_month="*"),  # every day
    },
    "delete_unused_attachments": {
        "task": "client.tasks.delete_unused_attachments",
        "schedule": crontab(minute="0", hour="*"),  # hour
    },
}

DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL", "")
EMAIL_HOST: str = os.getenv("EMAIL_HOST", "")
EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS: bool = bool(int(os.getenv("EMAIL_USE_TLS", 0)))
EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"

# OpenAI API settings
OPENAI_KEY: str = os.getenv("OPENAI_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

# Default tax
DEFAULT_TAX: int = 0  # 0%

VERSION: str = "0.0.1.a23"
