from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import Group
from authentication.models import CustomUser
from django.utils import timezone


class GroupMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)  # Can be null for immediate effect
    end_date = models.DateField(null=True, blank=True)  # Can be null for permanence

    def is_active(self):
        now = timezone.now().date()
        start_condition = (self.start_date is None or self.start_date <= now)
        end_condition = (self.end_date is None or self.end_date >= now)
        return start_condition and end_condition
    
    
    


    

