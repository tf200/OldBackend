# Create your models here.
from django.db import models
from django.utils import timezone

from authentication.models import CustomUser


class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.name

    def permissions_count(self) -> int:
        return self.permissions.count()


class GroupMembership(models.Model):  # this exists just for backward compatibility
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)  # Can be null for immediate effect
    end_date = models.DateField(null=True, blank=True)  # Can be null for permanence

    def is_active(self):
        now = timezone.now().date()
        start_condition = self.start_date is None or self.start_date <= now
        end_condition = self.end_date is None or self.end_date >= now
        return start_condition and end_condition

    is_active.boolean = True  # This will display as a boolean icon in the admin
    is_active.short_description = "Is active?"
