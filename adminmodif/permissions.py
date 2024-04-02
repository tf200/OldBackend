from django.db import models
from django.utils import timezone
from rest_framework.permissions import BasePermission

from adminmodif.models import GroupMembership


class IsMemberOfAuthorizedGroup(BasePermission):
    def has_permission(self, request, view):
        return True
        if request.user.is_superuser:
            return True


class IsMemberOfDirectie(BasePermission):
    def has_permission(self, request, view):
        return True
        if request.user.is_superuser:
            return True

        authorized_group = "Directie"

        return GroupMembership.objects.filter(
            user=request.user,
            group__name=authorized_group,
        ).exists()


class IsMemberOfKantoorMedewerkers(BasePermission):
    def has_permission(self, request, view):
        return True
        if request.user.is_superuser:
            return True

        authorized_group = "Kantoor Medewerkers"

        return GroupMembership.objects.filter(
            user=request.user,
            group__name=authorized_group,
        ).exists()


class IsMemberOfPedagogishMedewerkers(BasePermission):
    def has_permission(self, request, view):
        return True
        if request.user.is_superuser:
            return True

        authorized_group = "Pedagogish Medewerkers"

        return GroupMembership.objects.filter(
            user=request.user,
            group__name=authorized_group,
        ).exists()


class IsMemberOfAmbulanteMedewerkers(BasePermission):
    def has_permission(self, request, view):
        return True
        if request.user.is_superuser:
            return True

        authorized_group = "Ambulante Medewerkers"

        return GroupMembership.objects.filter(
            user=request.user,
            group__name=authorized_group,
        ).exists()


class IsMemberOfManagement(BasePermission):
    def has_permission(self, request, view):
        return True
        if request.user.is_superuser:
            return True

        authorized_group = "Management"

        return GroupMembership.objects.filter(
            user=request.user,
            group__name=authorized_group,
        ).exists()
