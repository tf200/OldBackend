import os

from celery import shared_task
from employees.models import ProgressReport
from system.utils import send_mail_async

from .models import ClientEmergencyContact


@shared_task
def send_progress_report_email(progress_report_id):
    try:
        progress_report = ProgressReport.objects.get(id=progress_report_id)
        emergency_contacts = ClientEmergencyContact.objects.filter(
            client=progress_report.client, auto_reports=True
        )

        for contact in emergency_contacts:
            send_mail_async.delay(
                subject="Progress Report Update",
                message="Here is the progress report...",
                from_email=None,
                recipient_list=[contact.email],
            )
    except ProgressReport.DoesNotExist:
        pass
