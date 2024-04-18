from __future__ import annotations

import os
import uuid

from django.conf import settings
from django.db import models
from loguru import logger

from system.utils import send_mail_async


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
        MEDICATION_TIME = "medication_time", "Medication Time"

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
    is_used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
