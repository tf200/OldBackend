import datetime
import calendar
from decimal import Decimal
import logging

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.utils import timezone
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import  status
from weasyprint import HTML

from celery import shared_task
from employees.models import Notification, ProgressReport

from .models import ClientEmergencyContact, Invoice, ClientDetails, Contract


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
def invoice_creation_per_month():
    today = datetime.date.today()
    start_date, _ = calendar.monthrange(today.year, today.month)
    end_date = today
    start_date = datetime.date(today.year, today.month, 1)
    end_date = datetime.date(today.year, today.month, end_date)

    client_ids = ClientDetails.objects.all().values_list("client_id", flat=True)
    for client_id in client_ids:
        try:

            client = ClientDetails.objects.get(id=client_id)
            contracts = Contract.objects.filter(client=client)
            if contracts.exists():
                client_type = contracts.first().sender
            else:
                # Handle the case where there are no contracts, perhaps set client_type to None or default
                client_type = None

            # Create an invoice instance
            invoice = Invoice(client=client, due_date=end_date)
            invoice.save()

            json_array = []
            for contract in contracts:
                contract_id = contract.id
                care_type = contract.care_type
                cost = Decimal(contract.calculate_cost_for_period(start_date, end_date))
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
                    "total_amount": float(total_amount),
                }

                # Adding the dictionary to our array
                json_array.append(contract_json)

                # Now you can safely create the InvoiceContract instance with Decimal values
            invoice.invoice_details = json_array

            # Saving the changes to the database

            # Calculate and update invoice totals based on the created InvoiceContract instances
            invoice.update_totals()
            invoice.save()

            # Prepare the context and generate the PDF
            context = {
                "invoice_contracts": json_array,
                "invoice": invoice,
                "company_name": client_type.name,
                "email": client_type.email_adress,
                "address": client_type.address,
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
            return "Processed clients successfully."
        except ClientDetails.DoesNotExist:
            logging.error(f"Client {client_id} not found.")
        except Exception as e:
            logging.error(f"Error processing client {client_id}: {e}")
            continue



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
    for invoice in invoices:
        if invoice.client.email:
            notification = Notification.objects.create(
                title="Invoice expired",
                event=Notification.EVENTS.INVOICE_EXPIRED,
                content=f"The invoice #{invoice.id} expired.",
                receiver=invoice.client.email,
            )

            notification.notify()
