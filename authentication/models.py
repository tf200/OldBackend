from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models

if TYPE_CHECKING:
    from client.models import ClientDetails
    from employees.models import EmployeeProfile


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    capacity = models.IntegerField(null=True)

    def get_total_expenses(self) -> float:
        return float(sum([expense.total_paid_amount() for expense in self.expenses.all()]))

    def get_total_revenue(self) -> float:
        from client.models import Contract

        self.client_location.values_list("id", flat=True).filter(
            contracts__care_type=Contract.CareTypes.ACCOMMODATION
        )
        return 0


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    phone_number = models.IntegerField(null=True, blank=True)

    def is_employee(self) -> bool:
        if hasattr(self, "profile"):
            # this is an employee
            return True
        return False

    def get_employee_profile(self) -> EmployeeProfile | None:
        if self.is_employee():
            # this is an employee
            return self.profile  # type: ignore
        return None

    def get_client_profile(self) -> ClientDetails | None:
        if not self.is_employee():
            # this is an employee
            return self.Client_Profile  # type: ignore
        return None


# Create your models here.
