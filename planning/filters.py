from django_filters import rest_framework as filters

from .models import Appointment


class AppointmentFilter(filters.FilterSet):
    # groups = filters.CharFilter(method='filter_groups')

    class Meta:
        model = Appointment
        fields = [
            "location",
        ]
