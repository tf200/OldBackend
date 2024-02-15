from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import Group
from authentication.models import CustomUser
from django.utils import timezone


class GroupMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def is_active(self):
        """Check if the group membership is currently active."""
        return self.start_date <= timezone.now().date() <= self.end_date

    def save(self, *args, **kwargs):
        """Override the save method to update group membership."""
        super(GroupMembership, self).save(*args, **kwargs)  # Call the "real" save() method.
        # Now we check the membership status and update the group accordingly.
        if self.is_active():
            self.group.user_set.add(self.user)
        else:
            self.group.user_set.remove(self.user)
