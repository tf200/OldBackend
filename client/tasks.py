import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from celery import shared_task
from employees.models import ProgressReport

from .models import ClientEmergencyContact, Invoice


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


@shared_task
def invoice_creation_per_month(progress_report_id, report_text):
    pass
    # This function runs every month to create invoices
    # This function should create invoices for each client to pay (or for each contract to be paid)?? you know the logic here


@shared_task
def invoice_mark_as_expired(progress_report_id, report_text):
    # Get all "outstanding" invoices more than 1 month
    one_month_datetime = timezone.now() - datetime.timedelta(days=30)
    invoices: list[Invoice] = Invoice.objects.filter(
        status="outstanding", due_date__gt=one_month_datetime
    ).all()

    # make it as "expired"
    for invoice in invoices:
        invoice.status = "expired"
        invoice.save()

    # send an email notification if needed to the invoice owner
