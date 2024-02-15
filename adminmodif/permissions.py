from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission
from adminmodif.models import GroupMembership
from django.utils import timezone

class IsMemberOfAuthorizedGroup(BasePermission):
    def has_permission(self, request, view):
        # Allow superusers to access every view
        if request.user.is_superuser:
            return True

        # Check if the user is in the specified group and within the valid date range
        authorized_group = 'AuthorizedGroupName'
        today = timezone.now().date()  # Adjust for DateField comparison
        return GroupMembership.objects.filter(
            user=request.user, 
            group__name=authorized_group, 
            start_date__lte=today, 
            end_date__gte=today
        ).exists()
