from django_filters import rest_framework as filters
from .models import ClientDiagnosis
from django_filters.filters import DateFilter , DateFromToRangeFilter



class ClientDiagnosisFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    diagnosis_code = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    severity = filters.CharFilter(lookup_expr='icontains')
    status = filters.CharFilter(lookup_expr='icontains')
    diagnosing_clinician = filters.CharFilter(lookup_expr='icontains')

    # Date filters
    date_of_diagnosis = DateFilter()
    date_of_diagnosis_range = DateFromToRangeFilter()
    date_of_diagnosis_year = DateFilter(field_name='date_of_diagnosis', lookup_expr='year')
    date_of_diagnosis_month = DateFilter(field_name='date_of_diagnosis', lookup_expr='month')
    date_of_diagnosis_day = DateFilter(field_name='date_of_diagnosis', lookup_expr='day')

    class Meta:
        model = ClientDiagnosis
        fields = ['title', 'diagnosis_code', 'description', 'severity', 'status', 
                  'diagnosing_clinician', 'date_of_diagnosis', 
                  'date_of_diagnosis_range', 'date_of_diagnosis_year', 
                  'date_of_diagnosis_month', 'date_of_diagnosis_day']