from django.db import models
from django.conf import settings


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
    sender = models.ForeignKey(ClientType, on_delete=models.CASCADE, related_name='clientsender')

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
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name='contracts')
    start_date = models.DateField(verbose_name="Date of Care Commencement")
    end_date = models.DateField(verbose_name="Date of Care Termination")
    care_type = models.CharField(max_length=100, verbose_name="Type of Care")
    rate_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Daily Rate")
    rate_per_minute = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Rate per Minute")
    rate_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Rate per Hour")
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


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

