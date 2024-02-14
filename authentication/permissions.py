from rest_framework.permissions import BasePermission

class IsMemberOfAuthorizedGroup(BasePermission):
    def has_permission(self, request, view):
        # Allow superusers to access every view
        if request.user.is_superuser:
            return True

        # Check if the user is in a group with the required permission
        return request.user.groups.filter(name='AuthorizedGroupName').exists()