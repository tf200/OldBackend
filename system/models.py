from __future__ import annotations

import datetime
import os
import random
import string
import uuid
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from loguru import logger

from authentication.models import Location
from system.utils import send_mail_async


class DBSettings(models.Model):
    _settings: dict[str, Any] | None = None

    class OptionTypes(models.TextChoices):
        STR = ("str", "string")
        INT = ("int", "integer")
        FLOAT = ("float", "float")
        BOOL = ("bool", "boolean")

    option_name = models.CharField(max_length=255, unique=True)
    option_value = models.CharField(default="", blank=True)
    option_type = models.CharField(choices=OptionTypes.choices, default=OptionTypes.STR)

    class Meta:
        ordering = ("id",)
        verbose_name = "DB Setting"

    @classmethod
    def get_settings(cls, refresh=False) -> dict[str, Any]:
        if cls._settings is None or refresh:
            cls._settings = {}

            # Fetch all the settings.
            options = cls.objects.all()
            for option in options:
                cls._settings[option.option_name.upper()] = cls.parse_value(option)

            # assign the version
            cls._settings["VERSION"] = settings.VERSION

        return cls._settings

    @classmethod
    def get(cls, key: str, default=None) -> Any:
        if cls._settings is None:
            cls.get_settings()

        if default is None:
            default = ""

        value = cls._settings.get(key, "")  # type: ignore

        return value if value != "" else default

    @classmethod
    def set(cls, key: str, value: Any):
        if cls.objects.filter(option_name=key).update(option_value=value):
            cls.get_settings(refresh=True)  # to refresh the _settings dict
            return True
        return False

    @classmethod
    def parse_value(cls, option: DBSettings) -> Any:
        if option.option_value:
            if option.option_type == cls.OptionTypes.INT:
                return int(option.option_value)
            if option.option_type == cls.OptionTypes.FLOAT:
                return float(option.option_value)
            if option.option_type == cls.OptionTypes.BOOL:
                return option.option_value in (1, "1", "true", "True", "TRUE")

        return str(option.option_value)


class Notification(models.Model):
    class EVENTS(models.TextChoices):
        NORMAL = "normal", "Normal"
        LOGIN_SEND_CREDENTIALS = "login_send_credentials", "Login - send credentials"
        APPOINTMENT_CREATED = "appointment_created", "Appointment - created"
        APPOINTMENT_UPDATED = "appointment_updated", "Appointment - updated"
        APPOINTMENT_RESCHEDULED = "appointment_rescheduled", "Appointment - rescheduled"
        APPOINTMENT_CANCELED = "appointment_canceled", "Appointment canceled"
        INVOICE_EXPIRED = "invoice_expired", "Invoice expired"
        INVOICE_CREATED = "invoice_created", "Invoice created"
        PROGRESS_REPORT_AVAILABLE = "progress_report_available", "Progress Report Available"
        PROGRESS_REPORT_CREATED = "progress_report_created", "Progress Report Created"
        MEDICATION_TIME = "medication_time", "Medication Time"
        CONTRACT_REMINDER = "contract_reminder", "Contract Reminder"

    event = models.CharField(choices=EVENTS.choices, default=EVENTS.NORMAL)
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def send_via_email(
        self,
        title: str | None = None,
        content: str | None = None,
        *,
        to: str | None = None,
        icon: str = "🔔",
    ) -> None:
        # Check if there is a receiver email first
        receiver_email: str | None = to if to is not None else self.get_receiver_email()

        if receiver_email is None or receiver_email == "":
            return None

        if title is None:
            title = self.title

        if content is None:
            content = self.content

        # Add an icon
        if icon is not None:
            title = f"{icon} {self.title}"

        logger.debug(f"Send a notification ({receiver_email}).")

        send_mail_async.delay(
            subject=title,
            message=content,
            from_email=None,  # the default will be used
            recipient_list=[receiver_email],
            fail_silently=True,
        )

    def get_receiver_email(self) -> str | None:
        if self.receiver:
            if hasattr(self.receiver, "profile"):
                # this is an employee
                return self.receiver.profile.email_address

            if hasattr(self.receiver, "Client_Profile"):
                # this is a client
                return self.receiver.Client_Profile.email
        return None

    def send_via_sms(
        self, title: str | None = None, content: str | None = None, icon: str = "🔔"
    ) -> None: ...

    def notify(
        self,
        email_title: str | None = None,
        email_content: str | None = None,
        *,
        to: str | None = None,
        icon: str = "🔔",
    ) -> None:
        """Notify receiver via email or SMS based on his preference,\n
        And should be dispatched once a notofication is created
        """

        title: str = self.title
        content: str = self.content
        email_address: str | None = None

        if email_title is not None:
            title = email_title

        if email_content is not None:
            content = email_content

        if to is not None:
            email_address = to

        self.send_via_email(title, content, to=email_address, icon=icon)
        self.send_via_sms(title, content, icon=icon)


def get_directory_path(instance: AttachmentFile, filename: str) -> str:
    ext = os.path.splitext(filename)[-1]
    return f"uploads/attachments/{instance.id}{ext}"


class AttachmentFile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=get_directory_path)
    size = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False, db_index=True)
    tag = models.CharField(max_length=100, default="", null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created",)

    def download_link(self) -> str:
        return self.file.url


class Expense(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)  # amount without TAX
    tax = models.FloatField(default=0)
    desc = models.TextField(default="", null=True, blank=True)
    attachment_ids = models.JSONField(default=list, blank=True)
    location = models.ForeignKey(
        Location, related_name="expenses", on_delete=models.SET_NULL, null=True
    )
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.desc} ({self.amount})"

    def total_paid_amount(self) -> Decimal:
        return self.amount * Decimal(1 + self.tax / 100)

    def __add__(self, other: Expense | int | float | Decimal) -> Decimal:
        if isinstance(other, Expense):
            return self.amount + other.amount
        if isinstance(other, (int, float)):
            return self.amount + Decimal(other)
        if isinstance(other, Decimal):
            return self.amount + other

    def __sub__(self, other: Expense | int | float | Decimal) -> Decimal:
        if isinstance(other, Expense):
            return self.amount - other.amount
        if isinstance(other, (int, float)):
            return self.amount - Decimal(other)
        if isinstance(other, Decimal):
            return self.amount - other

    def __mul__(self, other: Expense | int | float | Decimal) -> Decimal:
        if isinstance(other, Expense):
            return self.amount * other.amount
        if isinstance(other, (int, float)):
            return self.amount * Decimal(other)
        if isinstance(other, Decimal):
            return self.amount * other

    def __div__(self, other: Expense | int | float | Decimal) -> Decimal:
        if isinstance(other, Expense):
            return self.amount / other.amount
        if isinstance(other, (int, float)):
            return self.amount / Decimal(other)
        if isinstance(other, Decimal):
            return self.amount / other

    def __lt__(self, other: Expense | int | float | Decimal) -> bool:
        if isinstance(other, Expense):
            return self.amount < other.amount
        if isinstance(other, (int, float)):
            return self.amount < Decimal(other)
        if isinstance(other, Decimal):
            return self.amount < other

    def __le__(self, other: Expense | int | float | Decimal) -> bool:
        if isinstance(other, Expense):
            return self.amount <= other.amount
        if isinstance(other, (int, float)):
            return self.amount <= Decimal(other)
        if isinstance(other, Decimal):
            return self.amount <= other


def get_expiration_date() -> datetime.datetime:
    return timezone.now() + datetime.timedelta(days=settings.PROTECTED_EMAIL_EXPIRATION_DAYS)


# Create a protected Email model
class ProtectedEmail(models.Model):
    class EMAIL_TYPES(models.TextChoices):
        INCIDENT_REPORT = "incident_report", "Incident Report"
        MEDICAL_REPORT = "medical_report", "Medical Report"
        PROGRESS_REPORT = "progress_report", "Progress Report"

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True)
    email = models.EmailField()
    subject = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    email_type = models.CharField(choices=EMAIL_TYPES.choices)
    expired_at = models.DateTimeField(
        default=get_expiration_date, help_text="The date when the email will expire"
    )
    metadata = models.JSONField(default=dict, null=True, blank=True)
    passkey = models.CharField(max_length=30, default="")
    created = models.DateTimeField(auto_now_add=True)

    def notify(self, *, title: str | None = None, short_description: str | None = None) -> None:
        if title is None:
            title = ""
        if short_description is None:
            short_description = ""

        # Generate a passkey and save it
        self.passkey = self.generate_passkey()
        self.save()

        generated_link: str = self.generate_link()
        # the content should include the generated link as well as the passkey
        params: dict[str, Any] = {
            "title": title,
            "description": short_description,
            "passkey": self.passkey,
            "generated_link": generated_link,
            "expiration_date": self.expired_at,
            "company_name": DBSettings.get("CONTACT_COMPANY_NAME", ""),
        }

        content: str = render_to_string("email_templates/protected_email.html", params)

        # Send the email
        send_mail_async(
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject=self.subject,
            message=content,
            recipient_list=[self.email],
        )

    def generate_link(self) -> str:
        return f"{settings.FRONTEND_BASE_URL}/protected-email/{self.uuid}"

    def generate_passkey(self, max_length=8) -> str:
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=max_length))
