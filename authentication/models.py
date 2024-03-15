from django.db import models
from django.contrib.auth.models import AbstractUser













class Location(models.Model):
    name = models.CharField(max_length = 100)
    adress = models.CharField(max_length = 100)



class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.IntegerField(null= True , blank = True)
    
    





# Create your models here.
