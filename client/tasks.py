from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from employees.models import ProgressReport

from .models import ClientEmergencyContact


@shared_task
def send_progress_report_email(progress_report_id, report_text):
    try:

        progress_report = ProgressReport.objects.get(id=progress_report_id)

        emergency_contacts = ClientEmergencyContact.objects.filter(
            client=progress_report.client, auto_reports=True
        )

        for contact in emergency_contacts:
            send_mail(
                subject="Progress Report Update",
                message=f"{report_text}",
                recipient_list=[contact.email],
                fail_silently=False,
            )

        print("task finnished")
    except ProgressReport.DoesNotExist:
        pass
