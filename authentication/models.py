from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.IntegerField()
    



class adresses(models.Model):
    user = models.ForeignKey(CustomUser , on_delete = models.CASCADE)
    adress = models.CharField(max_length = 100)


# Create your models here.
