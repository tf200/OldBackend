from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission
from adminmodif.models import GroupMembership
from django.utils import timezone
from django.db import models

class IsMemberOfAuthorizedGroup(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        authorized_group = 'AuthorizedGroupName'
        today = timezone.now().date()
        # Query adjusted to accommodate immediate effect and permanence
        return GroupMembership.objects.filter(
            user=request.user,
            group__name=authorized_group,
            start_date__lte=today,  # Accounts for immediate effect by including null start_dates
        ).filter(
            models.Q(end_date__gte=today) | models.Q(end_date__isnull=True)  # Permanence for null end_dates
        ).exists()
