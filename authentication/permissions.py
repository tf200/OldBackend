from rest_framework.permissions import BasePermission

class IsMemberOfAuthorizedGroup(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is in a group with the required permission
        return request.user.groups.filter(name='AuthorizedGroupName').exists()