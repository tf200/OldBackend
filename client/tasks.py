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
from employees.models import (
    ClientMedication,
    ClientMedicationRecord,
    DomainGoal,
    GoalHistory,
    ObjectiveHistory,
    ProgressReport,
)
from system.models import AttachmentFile, Notification
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
            metadata={"report_id": progress_report.id},
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
    logger.debug("task: Create monthly invoices!")
    # Get all the current approved clients with a valid contract period
    clients = ClientDetails.objects.filter(status="In Care").all()

    for client in clients:
        invoice = client.generate_the_monthly_invoice()


# @shared_task
# def invoice_creation_per_month():
#     today = datetime.date.today()
#     start_date, _ = calendar.monthrange(today.year, today.month)
#     end_date = today
#     start_date = datetime.date(today.year, today.month, 1)
#     end_date = datetime.date(today.year, today.month, end_date.day)

#     clients = ClientDetails.objects.all()
#     for client in clients:
#         try:
#             contracts = Contract.objects.filter(client=client)
#             if contracts.exists():
#                 sender = contracts.first().sender
#             else:
#                 # Handle the case where there are no contracts, perhaps set sender to None or default
#                 sender = None

#             # Create an invoice instance
#             invoice = Invoice(client=client, due_date=end_date)
#             invoice.save()

#             json_array = []
#             for contract in contracts:
#                 contract_id = contract.id
#                 care_type = contract.care_type
#                 cost = Decimal(contract.calculate_cost_for_period(str(start_date), str(end_date)))
#                 vat_rate = Decimal(invoice.vat_rate)
#                 vat_amount = cost * (vat_rate / 100)
#                 total_amount = cost + vat_amount

#                 # Creating a dictionary for the current contract
#                 contract_json = {
#                     "contract": contract_id,
#                     "care_type": care_type,
#                     "pre_vat_total": float(
#                         cost
#                     ),  # JSON doesn't support Decimal, so we convert it to float
#                     "vat_rate": float(vat_rate),
#                     "vat_amount": float(vat_amount),
#                     "total_amount": float(total_amount),
#                 }

#                 # Adding the dictionary to our array
#                 json_array.append(contract_json)

#                 # Now you can safely create the InvoiceContract instance with Decimal values
#             invoice.invoice_details = json_array

#             # Saving the changes to the database

#             # Calculate and update invoice totals based on the created InvoiceContract instances
#             invoice.update_totals()
#             invoice.save()

#             logger.debug(f"Invoice created #{invoice.id}")

#             # Prepare the context and generate the PDF
#             context = {
#                 "invoice_contracts": json_array,
#                 "invoice": invoice,
#                 "company_name": sender.name if sender else "",
#                 "email": sender.email_adress if sender else "",
#                 "address": sender.address if sender else "",
#                 "vat_rate": invoice.vat_rate,
#                 "vat_amount": invoice.vat_amount,
#                 "total_amount": invoice.total_amount,
#                 "pre_vat_total": invoice.pre_vat_total,
#                 "issue_date": invoice.issue_date,
#                 "invoice_number": invoice.invoice_number,
#             }
#             html_string = render_to_string("invoice_template.html", context)
#             html = HTML(string=html_string)
#             pdf_content = html.write_pdf()
#             invoice_filename = f"invoice_{invoice.invoice_number}.pdf"

#             # Save the PDF content
#             if default_storage.exists(invoice_filename):
#                 default_storage.delete(invoice_filename)
#             default_storage.save(invoice_filename, ContentFile(pdf_content))

#             # Update the Invoice instance with the PDF URL
#             invoice_pdf_url = default_storage.url(invoice_filename)
#             invoice.url = invoice_pdf_url
#             invoice.save()

#             # ADD NOTIFICATIONS HERE
#             # send a notification to client
#             notification = Notification.objects.create(
#                 title="Invoice created",
#                 event=Notification.EVENTS.INVOICE_CREATED,
#                 content=f"You have a new invoice #{invoice.id} to be paid/resolved.",
#                 receiver=invoice.client.user,
#                 metadata={"invoice_id": invoice.id},
#             )

#             notification.notify()

#             # send a notification to sender
#             if sender and sender.email_adress:
#                 notification = Notification.objects.create(
#                     title="Invoice created",
#                     event=Notification.EVENTS.INVOICE_CREATED,
#                     content=f"You have a new invoice #{invoice.id} to be paid/resolved.",
#                     metadata={"invoice_id": invoice.id},
#                 )

#                 notification.notify(to=sender.email_adress)

#         except Exception as e:
#             logger.exception("Oops!")

#     logger.debug('"invoice_creation_per_month" task finished')

#     # This function runs every month to create invoices
#     # This function should create invoices for each client to pay (or for each contract to be paid)?? you know the logic here


@shared_task
def invoice_mark_as_expired():
    # Get all "outstanding" invoices more than 1 month
    # one_month_datetime = timezone.now() - datetime.timedelta(days=30)
    invoices: list[Invoice] = list(
        Invoice.objects.filter(status="outstanding", due_date__lt=timezone.now()).all()
    )

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
                metadata={"invoice_id": invoice.id},
            )

            notification.notify()


@shared_task
def invoice_send_notification_3_months_before():
    # Get all "outstanding" invoices more than 1 month
    three_months_before = timezone.now() - datetime.timedelta(days=30)
    invoices: list[Invoice] = list(
        Invoice.objects.filter(status="outstanding", due_date__gt=three_months_before).all()
    )

    # send an email notification if needed to the invoice owner
    for invoice in invoices:
        if invoice.client.email:
            notification = Notification.objects.create(
                title="Invoice notification",
                event=Notification.EVENTS.INVOICE_EXPIRED,
                content=f"You have an invoice to pay (#{invoice.pk}).",
                receiver=invoice.client.user,
                metadata={"invoice_id": invoice.pk},
            )

            notification.notify()


@shared_task
def create_and_send_medication_record_notification():
    current_date = timezone.now()
    ahead_datetime = current_date + datetime.timedelta(
        minutes=settings.MEDICATION_RECORDS_CREATATION
    )  # one hour ahead (and it should be the task interval)

    medications = ClientMedication.objects.filter(
        start_date__lte=current_date.date(), end_date__gte=current_date.date()
    ).all()

    created_medication_records: list[ClientMedicationRecord] = []

    # Create Medication Records when they get close (in time)
    for medication in medications:
        for slot in medication.get_available_slots():
            if current_date <= slot <= ahead_datetime:
                logger.debug(
                    f"{current_date} <= {slot} <= {ahead_datetime}: {(current_date <= slot <= ahead_datetime)}"
                )
                # Create a Medication record
                medication_record = ClientMedicationRecord.objects.create(
                    client_medication=medication,
                    time=slot,
                )
                logger.debug(f"Task: Medical Record Created #{medication_record.id}")
                created_medication_records.append(medication_record)

    # Send notifications
    for medication_record in created_medication_records:
        medication_record.notify()


@shared_task
def send_contract_reminders():
    logger.debug("Task: Sending contract reminders.")
    current_datetime = timezone.now()

    all_contracts = Contract.objects.filter(status=Contract.Status.APPROVED).all()
    available_contracts: list[Contract] = []

    # select the contracts that are going to expire
    for contract in all_contracts:
        date = (current_datetime + datetime.timedelta(days=contract.reminder_period)).date()

        if date == contract.end_date.date():
            available_contracts.append(contract)

    # Send notification reminder
    for contract in available_contracts:
        if contract.sender and contract.sender.email_adress:
            notification = Notification.objects.create(
                title="Contract reminder",
                event=Notification.EVENTS.CONTRACT_REMINDER,
                content=f"The contract #{contract.pk} is about to expire, make sure to renew it if needed.",
                metadata={"contract_id": contract.pk},
            )

            notification.notify(to=contract.sender.email_adress)


@shared_task
def mark_client_profile_as_in_care():
    logger.debug("Task: Mark Client Profile as 'In Care'")
    now = timezone.now()
    ClientDetails.objects.filter(
        status="On Waiting List",
        contracts__start_date__lte=now,
        contracts__end_date__gt=now,
        contracts__status=Contract.Status.APPROVED,
    ).update(status="In Care")


@shared_task
def delete_unused_attachments():
    logger.debug("Task: Delete unused attachment files.")
    AttachmentFile.objects.filter(
        is_used=False, created__lte=timezone.now() - datetime.timedelta(days=1)
    ).delete()


@shared_task
def record_goals_and_objectives_history():
    logger.debug("Task: record goals and objectives history.")
    # this function needs to be dispatched once everyday.
    now = timezone.now()
    for goal in DomainGoal.objects.all():
        # check if the current date has a record or not, if not then create one
        if not GoalHistory.objects.filter(date=now.date(), goal=goal).exists():
            GoalHistory.objects.create(rating=goal.main_goal_rating(), goal=goal)
            for objective in goal.objectives.all():  # type: ignore
                ObjectiveHistory.objects.create(rating=objective.rating, objective=objective)
