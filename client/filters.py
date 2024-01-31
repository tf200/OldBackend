from django_filters import rest_framework as filters
from .models import ClientDiagnosis



class ClientDiagnosisFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    diagnosis_code = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    severity = filters.CharFilter(lookup_expr='icontains')
    status = filters.CharFilter(lookup_expr='icontains')
    diagnosing_clinician = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ClientDiagnosis
        fields = ['title', 'diagnosis_code', 'description', 'severity', 'status', 'diagnosing_clinician']