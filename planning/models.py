from django.db import models
from  employees.models import EmployeeProfile
from client.models import ClientDetails
from django.utils.timezone import now
import uuid



# Create your models here.
class Appointment(models.Model):
    TYPE_CHOICES = (
        ('meeting', 'Meeting'),
        ('work', 'Work with Client'),
        ('other', 'Other'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    appointment_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    employees = models.ManyToManyField(EmployeeProfile, related_name='employee_appointments')  # Assuming Employee is a User
    clients = models.ManyToManyField(ClientDetails, related_name='client_appointments' ,blank=True)  # Reference to your Client model
    location = models.CharField(max_length=255, blank=True, null=True) 
    created_by = models.ForeignKey(EmployeeProfile, related_name='created_appointments', on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(EmployeeProfile, related_name='modified_appointments', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length = 50 , null = True , blank = True)

    def __str__(self):
        return self.title

# class AppointmentConfirmation(models.Model):
#     appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
#     employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
#     status = models.CharField(max_length=10, choices=(('confirmed', 'Confirmed'), ('refused', 'Refused')), default='confirmed')
#     date_responded = models.DateTimeField(default=now)

#     class Meta:
#         unique_together = ('appointment', 'employee')  # Ensure each employee responds only once per appointment

# Appointment.employees.through = AppointmentConfirmation

class TemporaryFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='temporary_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Temporary file {self.id} uploaded at {self.uploaded_at}"

class AppointmentAttachment(models.Model):
    appointment = models.ForeignKey(Appointment, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='appointment_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, help_text="Optional name for the file")

    def __str__(self):
        return self.name if self.name else f"Attachment for Appointment ID {self.appointment_id}"