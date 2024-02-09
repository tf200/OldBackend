from django_filters import rest_framework as filters
from .models import ClientDetails, ClientDiagnosis , ClientMedication , ClientAllergy
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


class ClientMedicationFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    dosage = filters.CharFilter(lookup_expr='icontains')
    frequency = filters.CharFilter(lookup_expr='icontains')
    start_date = filters.DateFilter()
    end_date = filters.DateFilter()
    notes = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ClientMedication
        fields = ['name', 'dosage', 'frequency', 'start_date', 'end_date', 'notes']
    



class ClientAllergyFilter(filters.FilterSet):
    allergy_type = filters.CharFilter(lookup_expr='icontains')
    severity = filters.CharFilter(lookup_expr='icontains')
    reaction = filters.CharFilter(lookup_expr='icontains')
    notes = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ClientAllergy
        fields = ['allergy_type', 'severity', 'reaction', 'notes']



class ClientDetailsFilter(filters.FilterSet):
    date_of_birth = DateFilter()
    date_of_birth_range = DateFromToRangeFilter()
    date_of_birth_year = DateFilter(field_name='date_of_birth', lookup_expr='year')
    date_of_birth_month = DateFilter(field_name='date_of_birth', lookup_expr='month')
    date_of_birth_day = DateFilter(field_name='date_of_birth', lookup_expr='day')

    class Meta:
        model = ClientDetails
        fields = {
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'date_of_birth': ['year__gt', 'year__lt'],
            'email': ['exact', 'icontains'],
            'phone_number': ['exact', 'icontains'],
            'organisation': ['exact', 'icontains'],
            'location': ['exact', 'icontains'],
            'departement': ['exact', 'icontains'],
            'gender': ['exact', 'icontains'],
            'filenumber': ['exact', 'gt', 'lt'],
            'city': ['exact', 'icontains'],
            'Zipcode': ['exact', 'icontains'],
            'infix': ['exact', 'icontains'],
            'streetname': ['exact', 'icontains'],
            'street_number': ['exact', 'icontains'],
        }
