from __future__ import annotations

import calendar
import os
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from loguru import logger
from weasyprint import HTML

from assessments.models import AssessmentDomain
from authentication.models import Location
from system.models import AttachmentFile, DBSettings, Notification


def generate_invoice_id() -> str:
    return os.urandom(4).hex().upper()


class Sender(models.Model):
    TYPE_CHOICES = [
        ("main_provider", "Main Provider"),
        ("local_authority", "Local Authority"),
        ("particular_party", "Particular Party"),
        ("healthcare_institution", "Healthcare Institution"),
    ]
    types = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    place = models.CharField(max_length=20, null=True, blank=True)
    land = models.CharField(max_length=20, null=True, blank=True)
    KVKnumber = models.CharField(max_length=20, null=True, blank=True)
    BTWnumber = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    client_number = models.CharField(max_length=20, null=True, blank=True)
    email_adress = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (#{self.pk})"


ClientType = Sender  # For backword compatibility


class ClientDetails(models.Model):
    Status = (
        ("In Care", "In Care"),
        ("On Waiting List", "On Waiting List"),
        ("Out Of Care", "Out Of Care"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="Client_Profile",
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    identity = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status,
        default="On Waiting List",
        blank=True,
        null=True,
    )
    bsn = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    birthplace = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    organisation = models.CharField(max_length=100, blank=True, null=True)
    departement = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    filenumber = models.IntegerField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="clients_pics/", blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    Zipcode = models.CharField(max_length=100, blank=True, null=True)
    infix = models.CharField(max_length=100, blank=True, null=True)
    streetname = models.CharField(max_length=100, blank=True, null=True)
    street_number = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    sender = models.ForeignKey(
        Sender, on_delete=models.CASCADE, related_name="clientsender", null=True
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, related_name="client_location", null=True
    )

    identity_attachment_ids = models.JSONField(default=list, blank=True)

    # class Meta:
    #     verbose_name = "Client"

    def generate_the_monthly_invoice(self, send_notifications=False) -> Invoice | None:
        """This function mush be called on once a month (to avoid invoice duplicate)."""
        # Get all client approved contracts
        current_date = timezone.now().date()
        contracts: list[Contract] = list(
            Contract.objects.filter(
                status=Contract.Status.APPROVED,
                start_date__lte=current_date,
                end_date__gte=current_date,
            ).all()
        )

        invoice_details = []
        total_amount: float = 0

        for contract in contracts:
            contract_amount: float = 0  # the contract amount for this month

            contract_amount_without_tax: float = contract.get_current_month_price(apply_tax=False)
            contract_amount = round(
                contract_amount_without_tax * (1 + contract.used_tax() / 100), 2
            )
            total_amount += contract_amount

            invoice_details.append(
                {
                    "contract_id": contract.pk,
                    "item_desc": f"Care: {contract.care_name} (contract: #{contract.id}, {contract.financing_act}/{contract.financing_option})",
                    "contract_amount": contract_amount,
                    "contract_amount_without_tax": contract_amount_without_tax,
                    "used_tax": contract.used_tax(),
                }
            )

        if invoice_details:
            # Create invoice for each all the available contracts
            invoice = Invoice.objects.create(
                client=self,
                total_amount=Decimal(total_amount),
                invoice_details=invoice_details,
                due_date=timezone.now() + timedelta(days=30),
            )

            # Send notifications
            if send_notifications:
                invoice.send_notification()

            return invoice
        return None

    def has_untaken_medications(self) -> int:
        from employees.models import ClientMedicationRecord

        return ClientMedicationRecord.objects.filter(
            client_medication__client=self, status=ClientMedicationRecord.Status.NOT_TAKEN
        ).count()

    def get_current_levels(self) -> list[ClientCurrentLevel]:
        current_levels: list[ClientCurrentLevel] = list(self.current_levels.all())
        # if not current_levels:
        #     domains = self.care_plans.all().values_list("domains", flat=True).distinct()
        #     for domain in domains:
        #         current_levels.append(
        #             ClientCurrentLevel.objects.create(
        #                 client=self, domain=domain
        #             )  # default level: 1
        #         )
        return current_levels

    def generate_profile_document_link(self) -> str:
        """Generate a Client profile PDF and return a downloadable link (please see the PDF templete for it)"""
        # Ensure to use "AttachmentFile" (in the system model)
        pass

    def save(self, *args, **kwargs):
        AttachmentFile.objects.filter(id__in=self.identity_attachment_ids).update(is_used=True)
        return super().save(*args, **kwargs)


class ClientCurrentLevel(models.Model):
    client = models.ForeignKey(
        ClientDetails, related_name="current_levels", on_delete=models.CASCADE
    )
    domain = models.ForeignKey(
        AssessmentDomain, related_name="current_levels", on_delete=models.CASCADE
    )
    level = models.IntegerField(default=1)  # levels 1 - 5

    def __str__(self) -> str:
        return f"Current level: {self.level}"


class ClientStatusHistory(models.Model):
    client = models.ForeignKey(
        ClientDetails, related_name="status_history", on_delete=models.CASCADE
    )
    status = models.CharField(choices=ClientDetails.Status)
    start_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return f"{self.status} (since: {self.start_date})"


class ClientState(models.Model):
    class Types(models.TextChoices):
        EMOTIONAL = ("emotional", "Emotional")
        PHYSICAL = ("physical", "Physical")

    value = models.IntegerField(default=0)
    type = models.CharField(choices=Types.choices)
    content = models.TextField(default="", null=True)

    client = models.ForeignKey(
        ClientDetails, related_name="client_states", on_delete=models.CASCADE
    )

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class ClientDiagnosis(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name="diagnoses")
    diagnosis_code = models.CharField(max_length=10)
    description = models.TextField()
    date_of_diagnosis = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=100)
    diagnosing_clinician = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class ClientEmergencyContact(models.Model):
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name="emergency_contact"
    )
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    relationship = models.CharField(max_length=100, blank=True, null=True)
    relation_status = models.CharField(
        max_length=50,
        choices=[
            ("Primary Relationship", "Primary Relationship"),
            ("Secondary Relationship", "Secondary Relationship"),
        ],
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    medical_reports = models.BooleanField(default=False)
    incidents_reports = models.BooleanField(default=False)
    goals_reports = models.BooleanField(default=False)


class Treatments(models.Model):
    user = models.ForeignKey(ClientDetails, related_name="treatments", on_delete=models.CASCADE)
    treatment_name = models.CharField(max_length=500)
    treatment_date = models.CharField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name} for {self.client.name}"


class ClientAllergy(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name="allergies")
    allergy_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=100)
    reaction = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.allergy_type} allergy for {self.client.name}"


class ClientDocuments(models.Model):
    user = models.ForeignKey(ClientDetails, related_name="documents", on_delete=models.CASCADE)
    documents = models.FileField(upload_to="client_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.original_filename = self.documents.name
            self.file_size = self.documents.file.size
        super(ClientDocuments, self).save(*args, **kwargs)


# TODO: Add some contract type seeds
class ContractType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name.title()


class Contract(models.Model):
    class CareTypes(models.TextChoices):
        AMBULANTE = "ambulante", "Ambulante"
        ACCOMMODATION = "accommodation", "Accommodation"

    class Frequency(models.TextChoices):
        MINUTE = "minute", "Minute"
        HOURLY = "hourly", "Hourly"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    class Status(models.TextChoices):
        APPROVED = ("approved", "Approved")
        DRAFT = ("draft", "Draft")
        TERMINATED = ("terminated", "Terminated")
        STOPPED = ("stopped", "Stopped")

    class HoursType(models.TextChoices):
        WEEKLY = ("weekly", "Weekly")
        ALL_PERIOD = ("all_period", "All Period")

    class FinancingActs(models.TextChoices):
        WMO = ("WMO", "WMO")
        ZVW = ("ZVW", "ZVW")
        WLZ = ("WLZ", "WLZ")
        JW = ("JW", "JW")
        WPG = ("WPG", "WPG")

    class FinancingOptions(models.TextChoices):
        ZIN = ("ZIN", "ZIN")
        PGB = ("PGB", "PGB")

    type = models.ForeignKey(ContractType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    reminder_period = models.IntegerField(default=10)  # in days
    tax = models.IntegerField(
        default=-1, null=True, blank=True
    )  # -1 means use the default Tax (20%) | 0 means tax exemption
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_frequency = models.CharField(choices=Frequency.choices, default=Frequency.WEEKLY)

    hours = models.IntegerField(default=0)
    hours_type = models.CharField(choices=HoursType.choices, default=HoursType.ALL_PERIOD)

    care_name = models.CharField(max_length=255)
    care_type = models.CharField(choices=CareTypes.choices)

    client = models.ForeignKey(ClientDetails, related_name="contracts", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        Sender, related_name="contracts", on_delete=models.SET_NULL, null=True, blank=True
    )

    attachment_ids = models.JSONField(default=list, blank=True)

    financing_act = models.CharField(choices=FinancingActs.choices, default=FinancingActs.WMO)
    financing_option = models.CharField(
        choices=FinancingOptions.choices, default=FinancingOptions.PGB
    )

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def save(self, *args, **kwargs):
        if self.pk:
            old_contract = get_object_or_404(Contact, id=self.pk)
            AttachmentFile.objects.filter(id__in=old_contract.attachment_ids).update(is_used=False)  # type: ignore

        # Mark attachments as used
        AttachmentFile.objects.filter(id__in=self.attachment_ids).update(is_used=True)

        return super().save(*args, **kwargs)

    def get_monthly_price(self) -> float:
        price: float = 0.0

        # current month
        now = timezone.now()
        current_month: int = now.month
        _, number_of_days_this_month = calendar.monthrange(now.year, current_month)

        if self.price_frequency == self.Frequency.MONTHLY:
            price = float(self.price)
        if self.price_frequency == self.Frequency.DAILY:
            price = float(self.price * Decimal(number_of_days_this_month))
        if self.price_frequency == self.Frequency.HOURLY:
            price = float(self.price * 24 * Decimal(number_of_days_this_month))
        if self.price_frequency == self.Frequency.MINUTE:
            price = float(self.price * 60 * 24 * Decimal(number_of_days_this_month))
        if self.price_frequency == self.Frequency.WEEKLY:
            price = float(self.price * Decimal(4.345))  # NOTE: 1 month = 4.345 weeks

        return price

    def clamp_period(self) -> tuple[datetime, datetime]:
        """Get only the involved duration/period of the month"""
        now = timezone.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0)
        _, number_of_days_this_month = calendar.monthrange(now.year, now.month)

        end_date = start_date.replace(day=number_of_days_this_month)

        if self.start_date > start_date:
            start_date = self.start_date

        if self.end_date < end_date:
            end_date = self.end_date

        return start_date, end_date

    def get_current_month_price_via_period(self, apply_tax=True) -> float:
        now = timezone.now()
        start_date, end_date = self.clamp_period()
        monthly_price = self.get_monthly_price()
        _, number_of_days_this_month = calendar.monthrange(now.year, now.month)

        price: float = (end_date - start_date).days * monthly_price / number_of_days_this_month

        # apply the task
        if apply_tax:
            return price * (1 - self.used_tax() / 100)

        return price

    def get_current_month_price_via_working_hours(self, apply_tax=True) -> float:
        start_date, end_date = self.clamp_period()

        working_hours: list[ContractWorkingHours] = list(
            self.working_hours.filter(  # type: ignore
                datetime__gte=start_date, datetime__lte=end_date
            ).all()
        )

        total_working_hours: float = (
            sum(w.minutes for w in working_hours) / 60
        )  # to convert from minutes to hours.
        price: float = 0

        if self.price_frequency == self.Frequency.HOURLY:
            price = float(self.price * Decimal(total_working_hours))
        if self.price_frequency == self.Frequency.MINUTE:
            price = float(self.price * 60 * Decimal(total_working_hours))

        # apply the task
        if apply_tax:
            return price * (1 - self.used_tax() / 100)

        return price

    def get_current_month_price(self, apply_tax=True) -> float:
        if self.type == Contract.CareTypes.ACCOMMODATION:
            return self.get_current_month_price_via_period(apply_tax=apply_tax)

        return self.get_current_month_price_via_working_hours(apply_tax=apply_tax)

    def used_tax(self) -> int:
        if self.tax is None or self.tax == -1:
            return settings.DEFAULT_TAX
        return self.tax

    def __str__(self):
        return f"Contract (#{self.pk})"


class ContractWorkingHours(models.Model):
    contract = models.ForeignKey(Contract, related_name="working_hours", on_delete=models.CASCADE)
    minutes = models.IntegerField(default=0)
    datetime = models.DateTimeField(default=timezone.now, db_index=True)
    notes = models.TextField(default="", null=True, blank=True)

    class Meta:
        ordering = ("datetime",)
        verbose_name = "Contract Working Hours"
        verbose_name_plural = "Contract Working Hours"


class Invoice(models.Model):
    class PaymentMethods(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CREDIT_CARD = "credit_card", "Credit Card"
        CHECK = "check", "Check"
        CASH = "cash", "Cash"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OUTSTANDING = ("outstanding", "Outstanding")
        PARTIALLY_PAID = ("partially_paid", "Partially Paid")
        PAID = ("paid", "Paid")
        EXPIRED = ("expired", "Expired")
        OVERPAID = ("overpaid", "Overpaid")
        IMPORTED = ("imported", "Imported")
        CONCEPT = ("concept", "Concept")

    invoice_number = models.CharField(
        max_length=10, default=generate_invoice_id, editable=False, unique=True, db_index=True
    )
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(choices=Status.choices, default=Status.CONCEPT)
    invoice_details = models.JSONField(default=list, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(0))
    pdf_attachment = models.OneToOneField(
        AttachmentFile, on_delete=models.SET_NULL, null=True, blank=True
    )
    extra_content = models.TextField(default="", null=True, blank=True)

    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def save(self, *args, **kwargs):
        if self.pk:
            old_invoice = self.__class__.objects.get(id=self.pk)
            if self.status == self.Status.OUTSTANDING and old_invoice.status == self.Status.CONCEPT:
                # Send notifications
                self.send_notification()

        return super().save(*args, **kwargs)

    def send_notification(self) -> None:
        logger.debug("Send invoice notification")
        # Send a notification to the client
        notification = Notification.objects.create(
            title="Invoice created",
            event=Notification.EVENTS.INVOICE_CREATED,
            content=f"You have a new invoice #{self.id} to be paid/resolved.",  # type: ignore
            receiver=self.client.user,
            metadata={"invoice_id": self.id},  # type: ignore
        )

        notification.notify()

        # TODO: Send a notification to the admin as well

        # send a notification to sender
        # if contract.sender and contract.sender.email_adress:
        #     notification = Notification.objects.create(
        #         title="Invoice created",
        #         event=Notification.EVENTS.INVOICE_CREATED,
        #         content=f"You have a new invoice #{self.id} to be paid/resolved.",  # type: ignore
        #         metadata={"invoice_id": self.id},  # type: ignore
        #     )

        #     notification.notify(to=contract.sender.email_adress)

    def total_paid_amount(self) -> float:
        # return round(sum([invoice_history.amount for invoice_history in self.history.all()]), 2)
        total: None | Decimal = (
            self.__class__.objects.filter(id=self.pk)
            .values_list("history__amount", flat=True)
            .aggregate(total=Sum("history__amount"))["total"]
        )

        if total:
            return float(total)
        return 0

    def refresh_total_amount(self, save: bool = True) -> None:
        # recalculating the amount every time/update
        self.total_amount = Decimal(
            sum([item["contract_amount"] for item in self.invoice_details])  # type: ignore
        )

        if save:
            self.save()
            # delete the old pdf attachment
            if self.pdf_attachment:
                self.pdf_attachment.delete()

    def download_link(self, refresh=False) -> str:
        """Ensure to generate an invoice PDF and return a link to download it"""
        """
        this is the structure of "self.invoice_details"
        {
            "contract_id": str,
            "item_desc": str,
            "contract_amount": float,
            "contract_amount_without_tax": float,
            "used_tax": int,
        }
        """
        # check if the PDF is already generated
        if self.pdf_attachment and refresh is False:
            return self.pdf_attachment.file.url

        sender = self.client.sender
        prefix_content: str = f"The {DBSettings.get(
                'CONTACT_COMPANY_NAME', DBSettings.get('SITE_NAME')
            )} provides care to the above-mentioned client, at a price of {DBSettings.get('SITE_CURRENCY_SYMBOL')} within this month ({self.due_date.strftime('%m/%Y')}). if the care process is terminated permaturely, billing will stop as of the end date of care."

        context = {
            "invoice_number": self.invoice_number,
            "invoice_contracts": self.invoice_details,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "total_amount": self.total_amount,
            "prefix_content": prefix_content,
            "extra_content": self.extra_content,
            # Client
            "client_full_name": f"{self.client.first_name} {self.client.last_name}",
            "client_id": self.client.id,
            "client_date_of_birth": self.client.date_of_birth,
            # Sender
            "company_name": sender.name if sender else "",
            "email": sender.email_adress if sender else "",
            "address": sender.address if sender else "",
            "KVK": sender.BTWnumber if sender else "",
            "BTW": sender.KVKnumber if sender else "",
            # Site info
            "site_name": DBSettings.get("SITE_NAME"),
            "invoice_footer": DBSettings.get("INVOICE_FOOTER"),
            "site_currency": DBSettings.get("SITE_CURRENCY"),
            "site_currency_symbol": DBSettings.get("SITE_CURRENCY_SYMBOL"),
            # Company info
            "invoice_company_name": DBSettings.get(
                "CONTACT_COMPANY_NAME", DBSettings.get("SITE_NAME")
            ),
            "invoice_email": DBSettings.get("CONTACT_EMAIL"),
            "invoice_address": DBSettings.get("CONTACT_ADDRESS"),
            "invoice_phone": DBSettings.get("CONTACT_PHONE"),
        }
        html_string = render_to_string("invoice_template.html", context)
        html = HTML(string=html_string)
        pdf_content = html.write_pdf()
        new_attachment = AttachmentFile()
        new_attachment.name = f"Invoice_{self.invoice_number}.pdf"
        new_attachment.file.save(
            new_attachment.name, ContentFile(pdf_content if pdf_content else "")
        )
        new_attachment.size = new_attachment.file.size
        new_attachment.is_used = True
        new_attachment.tag = "Invoice"
        new_attachment.save()

        # Assign the generated PDF.
        if self.pdf_attachment:
            self.pdf_attachment.delete()  # Delete the old one in case of refresh is True

        self.pdf_attachment = new_attachment

        return new_attachment.file.url


class InvoiceHistory(models.Model):
    class PaymentMethods(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CREDIT_CARD = "credit_card", "Credit Card"
        CHECK = "check", "Check"
        CASH = "cash", "Cash"
        OTHER = "other", "Other"

    payment_method = models.CharField(choices=PaymentMethods.choices, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(0))
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    invoice = models.ForeignKey(Invoice, related_name="history", on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created",)
        verbose_name_plural = "Invoice history"


# class Contract(models.Model):
#     sender = models.ForeignKey(Sender, on_delete=models.CASCADE, related_name="sender_contracts")
#     RATE_TYPE_CHOICES = (
#         ("day", "Per Day"),
#         ("week", "Per Week"),
#         ("hour", "Per Hour"),
#         ("minute", "Per Minute"),
#     )
#     client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name="contracts")
#     start_date = models.DateField(verbose_name="Date of Care Commencement")
#     duration_client = models.IntegerField(verbose_name="Duration in Months", null=True)
#     duration_sender = models.IntegerField(
#         verbose_name="Times per Year", null=True
#     )  # New field for duration
#     care_type = models.CharField(max_length=100, verbose_name="Type of Care")
#     rate_type = models.CharField(
#         max_length=10, choices=RATE_TYPE_CHOICES, verbose_name="Rate Type", null=True
#     )
#     rate_value = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         verbose_name="Rate Value",
#     )

#     contract_type = models.ForeignKey(
#         ContractType, related_name="contracts", on_delete=models.SET_NULL, null=True, blank=True
#     )

#     created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

#     def calculate_cost_for_period(self, start_date_str: str, end_date_str: str):
#         # Convert string dates to datetime objects
#         start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
#         end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

#         # Calculate the total duration in days
#         duration_in_days = (end_date - start_date).days + 1

#         # Ensure duration_in_days is a Decimal for arithmetic operations
#         duration_in_days_decimal = Decimal(duration_in_days)

#         # Calculate the cost based on the rate type
#         if self.rate_type == "day":
#             return duration_in_days_decimal * self.rate_value
#         elif self.rate_type == "week":
#             weeks = duration_in_days_decimal / Decimal(7)
#             return weeks * self.rate_value
#         elif self.rate_type == "hour":
#             hours = duration_in_days_decimal * Decimal(24)
#             return hours * self.rate_value
#         elif self.rate_type == "minute":
#             minutes = duration_in_days_decimal * Decimal(24) * Decimal(60)
#             return minutes * self.rate_value
#         else:
#             return Decimal(0)


class ContractAttachment(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Contract",
    )
    name = models.CharField(max_length=255, verbose_name="Attachment Name")
    attachment = models.FileField(upload_to="contract_attachments/", verbose_name="File")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.name} for {self.contract}"


class ClientAgreement(models.Model):
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="client_agreements"
    )
    agreement_details = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Client Agreement for {self.contract.client.name}"


class Provision(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="provisions")
    provision_details = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Provision for {self.contract.client.name}"


class FrameworkAgreement(models.Model):
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name="framework_agreements"
    )
    agreement_details = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


# class EmotionalState(models.Model):
#     client = models.ForeignKey(
#         ClientDetails, on_delete=models.CASCADE, related_name="client_emotional")
#     severity = models.CharField(max_length=50, blank=True, null=True)
#     date = models.DateTimeField()
#     state_description = models.TextField()
#     created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

#     def __str__(self):
#         return f"Emotional State for {self.client.name} - {self.date}"


# class PhysicalState(models.Model):
#     client = models.ForeignKey(
#         ClientDetails, on_delete=models.CASCADE, related_name="client_physical")
#     severity = models.CharField(max_length=50, blank=True, null=True)
#     date = models.DateTimeField()
#     symptoms = models.TextField()
#     created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

#     def __str__(self):
#         return f"Physical State for {self.client.name} - {self.date}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name


class SenderContactRelation(models.Model):
    client_type = models.ForeignKey(Sender, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)


class TemporaryFile(models.Model):
    id = models.CharField(primary_key=True, default=generate_invoice_id, editable=False)
    file = models.FileField(upload_to="temporary_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Temporary file "{self.id}" uploaded at "{self.uploaded_at}"'


# class Invoice(models.Model):
#     STATUS_CHOICES = (
#         ("outstanding", "Outstanding"),
#         ("partially_paid", "Partially Paid"),
#         ("paid", "Paid"),
#         ("douabtfull_uncollectible", "Douabtfull or Uncollectible"),
#         ("expired", "Expired"),
#         ("overpaid", "Overpaid"),
#         ("imported", "Imported"),
#         ("concept", "Concept"),
#     )
#     PAYMENT_TYPE_CHOICES = (
#         ("bank_transfer", "Bank Transfer"),
#         ("credit_card", "Credit Card"),
#         ("check", "Check"),
#         ("cash", "Cash"),
#     )
#     invoice_number = models.CharField(
#         max_length=10, default=generate_invoice_id, editable=False, unique=True
#     )
#     issue_date = models.DateField(auto_now_add=True)
#     due_date = models.DateField()

#     pre_vat_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)  # As a percentage
#     vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     total_amount = models.DecimalField(
#         max_digits=10, decimal_places=2, default=0.00
#     )  # Post-VAT total
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="concept")
#     url = models.URLField(max_length=200, blank=True, null=True)
#     payment_type = models.CharField(
#         max_length=50, choices=PAYMENT_TYPE_CHOICES, blank=True, null=True
#     )
#     client = models.ForeignKey(
#         ClientDetails, on_delete=models.CASCADE, related_name="client_invoice"
#     )
#     invoice_details = models.JSONField(null=True, blank=True)

#     updated = models.DateTimeField(auto_now=True, db_index=True)
#     created = models.DateTimeField(auto_now_add=True, db_index=True)

#     def update_totals(self):
#         logger.debug("self.invoice_details: %s" % self.invoice_details)
#         # Assuming invoice_details is a list of dictionaries
#         # Extract the pre_vat_total and total_amount values into NumPy arrays
#         pre_vat_totals = np.array([item["pre_vat_total"] for item in self.invoice_details])
#         total_amounts = np.array([item["total_amount"] for item in self.invoice_details])

#         # Compute the sums using NumPy and convert them back to Decimal for precision
#         pre_vat_total_sum = round(np.sum(pre_vat_totals), 2)
#         total_amount_sum = round(np.sum(total_amounts), 2)

#         self.pre_vat_total = pre_vat_total_sum
#         self.vat_amount = self.pre_vat_total * (self.vat_rate / 100)
#         self.total_amount = total_amount_sum

#         # Save the updated totals
#         self.save()


class InvoiceContract(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, related_name="invoice_contract"
    )
    contract = models.ForeignKey(
        Contract, on_delete=models.SET_NULL, null=True, related_name="contract_invoice"
    )
    pre_vat_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)  # As a percentage
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )  # Post-VAT total

    updated = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)


# class InvoiceService(models.Model):
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_services')
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     quantity = models.IntegerField(default=1)
#     rate = models.DecimalField(max_digits=10, decimal_places=2)  # Pre-VAT rate
#     vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # As a percentage
#     total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Pre-VAT total

#     def calculate_total(self):
#         self.total = self.quantity * self.rate  # Update this if needed to include VAT calculation

#     def __str__(self):
#         return f"{self.service.name} on Invoice {self.invoice.invoice_number}"


class CarePlan(models.Model):
    client = models.ForeignKey(
        ClientDetails, related_name="care_plans", on_delete=models.SET_NULL, null=True
    )
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    domains = models.ManyToManyField(AssessmentDomain, related_name="care_plans")


class CareplanAtachements(models.Model):
    careplan = models.ForeignKey(
        CarePlan, on_delete=models.SET_NULL, null=True, related_name="care_attachement"
    )
    attachement = models.FileField(upload_to="clients_pics/")
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(null=True, max_length=100)
