from __future__ import annotations

import calendar
import os
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from loguru import logger

from assessments.models import AssessmentDomain
from authentication.models import Location
from system.models import AttachmentFile, Notification


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

    # class Meta:
    #     verbose_name = "Client"

    def generate_the_monthly_invoice(self, send_notifications=True) -> Invoice:
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
                    "item_desc": f"Care: {contract.care_name} (contract id: #{contract.id})",
                    "contract_amount": contract_amount,
                    "contract_amount_without_tax": contract_amount_without_tax,
                    "used_tax": contract.used_tax(),
                }
            )

        # Create invoice for each all the available contracts
        invoice = Invoice.objects.create(
            client=self,
            total_amount=Decimal(total_amount),
            invoice_details=invoice_details,
            due_date=timezone.now() + timedelta(days=30),
        )

        # Send notifications
        if send_notifications:
            for contract in contracts:
                # Send a notification to the client
                notification = Notification.objects.create(
                    title="Invoice created",
                    event=Notification.EVENTS.INVOICE_CREATED,
                    content=f"You have a new invoice #{invoice.id} to be paid/resolved.",  # type: ignore
                    receiver=invoice.client.user,
                    metadata={"invoice_id": invoice.id},  # type: ignore
                )

                notification.notify()

                # send a notification to sender
                if contract.sender and contract.sender.email_adress:
                    notification = Notification.objects.create(
                        title="Invoice created",
                        event=Notification.EVENTS.INVOICE_CREATED,
                        content=f"You have a new invoice #{invoice.id} to be paid/resolved.",  # type: ignore
                        metadata={"invoice_id": invoice.id},  # type: ignore
                    )

                    notification.notify(to=contract.sender.email_adress)

        return invoice

    def has_untaken_medications(self) -> int:
        from employees.models import ClientMedicationRecord

        return ClientMedicationRecord.objects.filter(
            client_medication__client=self, status=ClientMedicationRecord.Status.NOT_TAKEN
        ).count()

    def generate_profile_document_link(self) -> str:
        """Generate a Client profile PDF and return a downloadable link (please see the PDF templete for it)"""
        # Ensure to use "AttachmentFile" (in the system model)
        pass


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

    class HoursType(models.TextChoices):
        WEEKLY = ("weekly", "Weekly")
        ALL_PERIOD = ("all_period", "All Period")

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

    attachment_ids = models.JSONField(default=list)

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
        max_length=10, default=generate_invoice_id, editable=False, unique=True
    )
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(choices=Status.choices, default=Status.CONCEPT)
    invoice_details = models.JSONField(default=list, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(0))

    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def total_paid_amount(self) -> float:
        return round(sum([invoice_history.amount for invoice_history in self.history.all()]), 2)

    def refresh_total_amount(self, save: bool = True) -> None:
        # recalculating the amount every time/update
        self.total_amount = Decimal(
            sum([item["contract_amount"] for item in self.invoice_details])  # type: ignore
        )

        if save:
            self.save()

    def download_link(self) -> str:
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
        pass


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
    client = models.ForeignKey(ClientDetails, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    domains = models.ManyToManyField(AssessmentDomain, related_name="care_plans")


class DomainGoal(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField(default="", null=True, blank=True)

    domain = models.ForeignKey(AssessmentDomain, related_name="goals", on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Main Goal: {self.title}"

    def total_objectives(self) -> int:
        return self.objectives.count()

    def main_goal_rating(self) -> float:
        """This average is calculated based on Objectives"""
        objectives = self.objectives.all()
        if objectives:
            return round(sum([objective.rating for objective in objectives]) / len(objectives), 1)
        return 0


class DomainObjective(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField(default="", null=True, blank=True)
    rating = models.FloatField(default=0)

    goal = models.ForeignKey(DomainGoal, related_name="objectives", on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Objective: {self.title}"


class CareplanAtachements(models.Model):
    careplan = models.ForeignKey(
        CarePlan, on_delete=models.SET_NULL, null=True, related_name="care_attachement"
    )
    attachement = models.FileField(upload_to="clients_pics/")
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(null=True, max_length=100)
