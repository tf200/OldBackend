from django.db import models
from authentication.models import CustomUser
from django.conf import settings

class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    # Professional Information
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







# Create your models here.
