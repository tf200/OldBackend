from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import uuid
from datetime import datetime
class ClientType (models.Model):
    TYPE_CHOICES = [
        ('main_provider', 'Main Provider'),
        ('local_authority', 'Local Authority'),
        ('particular_party', 'Particular Party'),
        ('healthcare_institution', 'Healthcare Institution'),
    ]
    types = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField (max_length=20)
    address  = models.CharField (max_length=200 , null = True , blank = True)
    postal_code = models.CharField (max_length=20 , null = True , blank = True)
    place = models.CharField (max_length=20 , null = True , blank = True)
    land = models.CharField (max_length=20 , null = True , blank = True)
    KVKnumber = models.CharField (max_length=20 , null = True , blank = True)
    BTWnumber = models.CharField (max_length=20 , null = True , blank = True)
    phone_number = models.CharField (max_length=20 , null = True , blank = True)
    client_number =models.CharField (max_length=20 , null = True , blank = True)
    email_adress = models.CharField (max_length=20 , null = True , blank = True)


class ClientDetails(models.Model):
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Client-Profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    identity = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=(('In Care', 'In Care'), ('On Waiting List',
                              'On Waiting List'), ('Out Of Concern', 'Out Of Concern')), default='On Waiting List', blank=True, null=True)
    bsn = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    birthplace = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    organisation = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    departement = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    filenumber = models.IntegerField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='clients_pics/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    Zipcode = models.CharField(max_length=100, blank=True, null=True)
    infix = models.CharField(max_length=100, blank=True, null=True)
    streetname = models.CharField(max_length=100, blank=True, null=True)
    street_number = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    sender = models.ForeignKey(ClientType, on_delete=models.CASCADE, related_name='clientsender' , null = True)

class ClientDiagnosis(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name='diagnoses')
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
        ClientDetails, on_delete=models.CASCADE, related_name='emergency_contact')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    relationship = models.CharField(max_length=100, blank=True, null=True)
    auto_reports = models.BooleanField(default=False)
    relation_status = models.CharField(max_length=50,  choices=[(
        'Primary Relationship', 'Primary Relationship'), ('Secondary Relationship', 'Secondary Relationship')], null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Treatments(models.Model):
    user = models.ForeignKey(
        ClientDetails, related_name='treatments', on_delete=models.CASCADE)
    treatment_name = models.CharField(max_length=500)
    treatment_date = models.CharField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)




    def __str__(self):
        return f"{self.name} for {self.client.name}"


class ClientAllergy(models.Model):
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name='allergies')
    allergy_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=100)
    reaction = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.allergy_type} allergy for {self.client.name}"




class ClientDocuments(models.Model):
    user = models.ForeignKey(
        ClientDetails, related_name='documents', on_delete=models.CASCADE)
    documents = models.FileField(upload_to='client_documents/')
    uploaded_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.original_filename = self.documents.name
            self.file_size = self.documents.file.size
        super(ClientDocuments, self).save(*args, **kwargs)


class Contract(models.Model):
    sender = models.ForeignKey(
        ClientType, on_delete=models.CASCADE, related_name='sender_contracts')
    RATE_TYPE_CHOICES = (
        ('day', 'Per Day'),
        ('week', 'Per Week'),
        ('hour', 'Per Hour'),
        ('minute', 'Per Minute'),
    )
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name='contracts')
    start_date = models.DateField(verbose_name="Date of Care Commencement")
    duration_client = models.IntegerField(verbose_name="Duration in Months" , null=True) 
    duration_sender = models.IntegerField(verbose_name="Times per Year" , null=True) # New field for duration
    care_type = models.CharField(max_length=100, verbose_name="Type of Care")
    rate_type = models.CharField(
        max_length=10, choices=RATE_TYPE_CHOICES, verbose_name="Rate Type", null=True)
    rate_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Rate Value")
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def calculate_cost_for_period(self, start_date_str, end_date_str):
        print(self.id)
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        # Calculate the total duration in days
        duration_in_days = (end_date - start_date).days + 1

        # Calculate the cost based on the rate type
        if self.rate_type == 'day':
            return duration_in_days * self.rate_value
        elif self.rate_type == 'week':
            weeks = duration_in_days / 7
            return weeks * self.rate_value
        elif self.rate_type == 'hour':
            hours = duration_in_days * 24
            return hours * self.rate_value
        elif self.rate_type == 'minute':
            minutes = duration_in_days * 24 * 60
            print(minutes * self.rate_value)
            return minutes * self.rate_value
        else:
            return 0

class ContractAttachment(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Contract"
    )
    name = models.CharField(max_length=255, verbose_name="Attachment Name")
    attachment = models.FileField(upload_to='contract_attachments/', verbose_name="File")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.name} for {self.contract}"



class ClientAgreement(models.Model):
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name='client_agreements')
    agreement_details = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Client Agreement for {self.contract.client.name}"


class Provision(models.Model):
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name='provisions')
    provision_details = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Provision for {self.contract.client.name}"


class FrameworkAgreement(models.Model):
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name='framework_agreements')
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




class ClientTypeContactRelation(models.Model):
    client_type = models.ForeignKey(ClientType, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    

class TemporaryFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='temporary_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Temporary file {self.id} uploaded at {self.uploaded_at}"


class Invoice(models.Model):
    invoice_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='invoices')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    pre_vat_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)  # As a percentage
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Post-VAT total
    status = models.CharField(max_length=50, choices=(('outstanding', 'Outstanding'), ('partially_paid', 'Partially Paid'), ('paid', 'Paid')))

    def calculate_totals(self):
        # Assuming the total cost calculation is based on the contract's details
     # Use the total_cost property from the Contract model
        
        # Calculate VAT and total amount
        self.vat_amount = (self.pre_vat_total * self.vat_rate) / 100

        self.total_amount = self.pre_vat_total + self.vat_amount

        self.save()


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

