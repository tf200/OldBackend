import calendar
import datetime
import logging
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.utils import timezone
from loguru import logger
from rest_framework import status
from rest_framework.response import Response
from weasyprint import HTML

from celery import shared_task
from employees.models import ClientMedication, ClientMedicationRecord, ProgressReport
from system.models import Notification
from system.utils import send_mail_async

from .models import ClientDetails, ClientEmergencyContact, Contract, Invoice


@shared_task
def send_progress_report_email(progress_report_id, report_text):
    try:
        progress_report = ProgressReport.objects.get(id=progress_report_id)

        emergency_contacts = ClientEmergencyContact.objects.filter(
            client=progress_report.client, auto_reports=True
        )

        notification = Notification.objects.create(
            title="Progress Report Update",
            event=Notification.EVENTS.PROGRESS_REPORT_AVAILABLE,
            content=f"You have a new progress report available #{progress_report.id}.",
            receiver=progress_report.client.user,
        )

        notification.notify()

        for contact in emergency_contacts:
            send_mail_async.delay(
                subject="Progress Report Update",
                message=f"{report_text}",
                from_email=None,
                recipient_list=[contact.email],
                fail_silently=False,
            )
    except ProgressReport.DoesNotExist:
        pass


@shared_task
def invoice_creation_per_month():
    today = datetime.date.today()
    start_date, _ = calendar.monthrange(today.year, today.month)
    end_date = today
    start_date = datetime.date(today.year, today.month, 1)
    end_date = datetime.date(today.year, today.month, end_date.day)

    clients = ClientDetails.objects.all()
    for client in clients:
        try:
            contracts = Contract.objects.filter(client=client)
            if contracts.exists():
                sender = contracts.first().sender
            else:
                # Handle the case where there are no contracts, perhaps set sender to None or default
                sender = None

            # Create an invoice instance
            invoice = Invoice(client=client, due_date=end_date)
            invoice.save()

            json_array = []
            for contract in contracts:
                contract_id = contract.id
                care_type = contract.care_type
                cost = Decimal(contract.calculate_cost_for_period(str(start_date), str(end_date)))
                vat_rate = Decimal(invoice.vat_rate)
                vat_amount = cost * (vat_rate / 100)
                total_amount = cost + vat_amount

                # Creating a dictionary for the current contract
                contract_json = {
                    "contract": contract_id,
                    "care_type": care_type,
                    "pre_vat_total": float(
                        cost
                    ),  # JSON doesn't support Decimal, so we convert it to float
                    "vat_rate": float(vat_rate),
                    "vat_amount": float(vat_amount),
                }

                # Adding the dictionary to our array
                json_array.append(contract_json)

                # Now you can safely create the InvoiceContract instance with Decimal values
            invoice.invoice_details = json_array

            # Saving the changes to the database

            # Calculate and update invoice totals based on the created InvoiceContract instances
            invoice.update_totals()
            invoice.save()

            logger.debug(f"Invoice created #{invoice.id}")

            # Prepare the context and generate the PDF
            context = {
                "invoice_contracts": json_array,
                "invoice": invoice,
                "company_name": sender.name if sender else "",
                "email": sender.email_adress if sender else "",
                "address": sender.address if sender else "",
                "vat_rate": invoice.vat_rate,
                "vat_amount": invoice.vat_amount,
                "total_amount": invoice.total_amount,
                "pre_vat_total": invoice.pre_vat_total,
                "issue_date": invoice.issue_date,
                "invoice_number": invoice.invoice_number,
            }
            html_string = render_to_string("invoice_template.html", context)
            html = HTML(string=html_string)
            pdf_content = html.write_pdf()
            invoice_filename = f"invoice_{invoice.invoice_number}.pdf"

            # Save the PDF content
            if default_storage.exists(invoice_filename):
                default_storage.delete(invoice_filename)
            default_storage.save(invoice_filename, ContentFile(pdf_content))

            # Update the Invoice instance with the PDF URL
            invoice_pdf_url = default_storage.url(invoice_filename)
            invoice.url = invoice_pdf_url
            invoice.save()

            # ADD NOTIFICATIONS HERE
            # send a notification to client
            notification = Notification.objects.create(
                title="Invoice created",
                event=Notification.EVENTS.INVOICE_CREATED,
                content=f"You have a new invoice #{invoice.id} to be paid/resolved.",
                receiver=invoice.client.user,
            )

            notification.notify()

            # send a notification to sender
            if sender:
                notification = Notification.objects.create(
                    title="Invoice created",
                    event=Notification.EVENTS.INVOICE_CREATED,
                    content=f"You have a new invoice #{invoice.id} to be paid/resolved.",
                    receiver=sender,
                )

                notification.notify()

        except Exception as e:
            logger.exception("Oops!")

    logger.debug('"invoice_creation_per_month" task finished')

    # This function runs every month to create invoices
    # This function should create invoices for each client to pay (or for each contract to be paid)?? you know the logic here


@shared_task
def invoice_mark_as_expired():
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
    for invoice in invoices:
        if invoice.client.email:
            notification = Notification.objects.create(
                title="Invoice expired",
                event=Notification.EVENTS.INVOICE_EXPIRED,
                content=f"The invoice #{invoice.id} expired.",
                receiver=invoice.client.email,
            )

            notification.notify()


@shared_task
def invoice_send_notification_3_months_before():
    # Get all "outstanding" invoices more than 1 month
    three_months_before = timezone.now() - datetime.timedelta(months=3)
    invoices: list[Invoice] = Invoice.objects.filter(
        status="outstanding", due_date__gt=three_months_before
    ).all()

    # send an email notification if needed to the invoice owner
    for invoice in invoices:
        if invoice.client.email:
            notification = Notification.objects.create(
                title="Invoice notification",
                event=Notification.EVENTS.INVOICE_EXPIRED,
                content=f"You have an invoice to pay (#{invoice.id}).",
                receiver=invoice.client.user,
            )

            notification.notify()


@shared_task
def create_and_send_medication_record_notification():
    current_date = timezone.now()
    ahead_datetime = current_date + datetime.timedelta(
        minutes=settings.MEDICATION_RECORDS_CREATATION
    )  # one hour ahead (and it should be the task interval)

    # client_medication_records = ClientMedicationRecord.objects.filter(
    #     time__gte=current_date, time__lt=ahead_datetime
    # ).all()

    # for medication_record in client_medication_records:
    #     medication_record.notify()

    medications = ClientMedication.objects.filter(
        start_date__lte=current_date.date(), end_date__gte=current_date.date()
    ).all()

    created_medication_records: list[ClientMedicationRecord] = []

    # Create Medication Records when they get close (in time)
    for medication in medications:
        for slot in medication.get_available_slots():
            logger.debug(
                f"{current_date} <= {slot} < {ahead_datetime}: {(current_date <= slot < ahead_datetime)}"
            )
            if current_date <= slot < ahead_datetime:
                # Create a Medication record
                medication_record = ClientMedicationRecord.objects.create(
                    client_medication=medication,
                    time=slot,
                )
                logger.debug(f"Medical Record Created #{medication_record.id}")
                created_medication_records.append(medication_record)

    # Send notifications
    for medication_record in created_medication_records:
        medication_record.notify()
