from django.db import models
from authentication.models import CustomUser





class ClientDetails(models.Model):
    firt_name = models.CharField(max_length = 100, blank= True , null = True)
    last_name = models.CharField(max_length = 100, blank= True , null = True)
    email = models.CharField(max_length = 100, blank= True , null = True)
    organisation = models.CharField(max_length = 100, blank= True , null = True)
    location = models.CharField(max_length=100, blank= True , null = True)
    departement= models.CharField(max_length=100, blank= True , null = True)
    gender = models.CharField(max_length = 100, blank= True , null = True)
    filenumber = models.IntegerField()

class ClientDiagnosis(models.Model):
    title = models.CharField(max_length = 50 , blank= True , null = True)
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis_code = models.CharField(max_length=10)  # Adjust length based on coding system
    description = models.TextField()
    date_of_diagnosis = models.DateField()
    severity = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=100)  # e.g., 'current', 'in remission', etc.
    diagnosing_clinician = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)




class Treatments(models.Model) : 
    user= models.ForeignKey(ClientDetails , related_name='treatments', on_delete = models.CASCADE)
    treatment_name = models.CharField(max_length = 500 )
    treatment_date = models.CharField()


class ClientDocuments(models.Model) : 
    user= models.ForeignKey(ClientDetails , related_name='documents' , on_delete = models.CASCADE)
    documents = models.FileField(upload_to='client_documents/')

class Contract(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name='contracts')
    start_date = models.DateField(verbose_name="Date of Care Commencement")
    end_date = models.DateField(verbose_name="Date of Care Termination")
    care_type = models.CharField(max_length=100, verbose_name="Type of Care")
    rate_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Daily Rate")
    rate_per_minute = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Rate per Minute")
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Rate per Hour")


class ClientAgreement(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='client_agreements')
    agreement_details = models.TextField()

    def __str__(self):
        return f"Client Agreement for {self.contract.client.name}"

class Provision(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='provisions')
    provision_details = models.TextField()

    def __str__(self):
        return f"Provision for {self.contract.client.name}"

class FrameworkAgreement(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name='framework_agreements')
    agreement_details = models.TextField()



class ProgressReport(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField()
    report_text = models.TextField()


class Measurement(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField()
    measurement_type = models.CharField(max_length=100)
    value = models.FloatField()

class Observations(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField()
    observation_text = models.TextField()

class Feedback(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField()
    feedback_text = models.TextField()


class EmotionalState(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateTimeField()
    state_description = models.TextField()
    intensity = models.IntegerField()  # You can use a scale like 1-10

    def __str__(self):
        return f"Emotional State for {self.client.name} - {self.date}"

class PhysicalState(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateTimeField()
    symptoms = models.TextField()
    severity = models.IntegerField()  # You can use a scale like 1-10

    def __str__(self):
        return f"Physical State for {self.client.name} - {self.date}"