from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings

from system.models import DBSettings, Notification

if TYPE_CHECKING:
    from employees.models import EmployeeProfile


def send_login_credentials(employee: EmployeeProfile, username, password):
    subject = "Your account credientials for " + DBSettings.get("SITE_NAME", "")
    message = f"Hello,\n\nYour account has been created, and there is your login credentials:\n\nLink: {settings.FRONTEND_BASE_URL}\n\nUsername: {username}\nPassword: {password}\n\nPlease change your password upon first login."

    notification = Notification.objects.create(
        title="Login credentials",
        event=Notification.EVENTS.LOGIN_SEND_CREDENTIALS,
        content="Login credentials are sent to your contacts (e.g email).",
        receiver=employee.user,
        metadata={"user_id": employee.user.id},
    )

    notification.notify(
        email_title=subject, email_content=message, to=employee.email_address
    )  # send email as well as SMS (in the future)
