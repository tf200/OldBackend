from django.db import models
from authentication.models import CustomUser
from django.conf import settings
from client.models import ClientDetails
from django.core.exceptions import ValidationError


class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    # Education
    highest_education = models.CharField(max_length=100)
    university = models.CharField(max_length=100, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    # Certifications
    certifications = models.TextField(help_text='List of certifications', null=True, blank=True)
    # Relevant Work Experience
    experience = models.TextField(help_text='List of relevant work experiences', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s Profile"





class Assignment(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='assignments')
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name='assigned_employees')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('Confirmed', 'Confirmed'), ('Pending', 'Pending'), ('Cancelled', 'Cancelled')])

    def __str__(self):
        return f"{self.employee} assigned to {self.client} from {self.start_datetime} to {self.end_datetime}"

    def clean(self):
        # Check for time conflicts
        overlapping_assignments = Assignment.objects.filter(
            employee=self.employee,
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime
        )
        if overlapping_assignments.exists():
            raise ValidationError("This assignment overlaps with another.")

        # Check if the employee is available
        if not self.employee.availabilities.filter(start_datetime__lte=self.start_datetime, end_datetime__gte=self.end_datetime).exists():
            raise ValidationError("The employee is not available at this time.")

        # Check if employee's skills match client's requirements
        if not self.employee.skills.filter(id__in=self.client.required_skills.all()).exists():
            raise ValidationError("The employee does not have the required skills for this client.")


class ProgressReport(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    report_text = models.TextField()





        





        



