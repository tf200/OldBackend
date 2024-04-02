from django.contrib.auth.models import AbstractUser
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    capacity = models.IntegerField(null=True)


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    phone_number = models.IntegerField(null=True, blank=True)


# Create your models here.
