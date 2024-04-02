from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EmployeeProfile

# @receiver(post_save, sender=get_user_model())
# def create_employee_profile(sender, instance, created, **kwargs):
#     if created:
#         EmployeeProfile.objects.create(user=instance)
