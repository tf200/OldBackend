from django_filters import rest_framework as filters
from django.contrib.auth.models import User
from .models import EmployeeProfile

class EmployeeProfileFilter(filters.FilterSet):
    # groups = filters.CharFilter(method='filter_groups')

    class Meta:
        model = EmployeeProfile
        fields = [
            'first_name',
            'last_name',
            # Add other fields you want to filter by
            'employee_number',
            'employment_number',
            'email_address',
            'private_email_address',
            'work_phone_number',
            'private_phone_number',
            'home_telephone_number',
            'gender',
            'location': ['exact'],
            # Note: 'groups' is handled separately via a method filter
        ]

    # def filter_groups(self, queryset, name, value):
    #     group_names = value.split(',')  # Split the comma-separated group names
    #     return queryset.filter(user__groups__name__in=group_names).distinct()