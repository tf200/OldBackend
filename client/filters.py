from datetime import datetime
from typing import Literal, Optional

import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.filters import CharFilter, DateFilter, DateFromToRangeFilter
from ninja import Field, FilterSchema

from employees.models import ClientMedication

from .models import ClientAllergy, ClientDetails, ClientDiagnosis, Invoice


class ClientDiagnosisFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    diagnosis_code = filters.CharFilter(lookup_expr="icontains")
    description = filters.CharFilter(lookup_expr="icontains")
    severity = filters.CharFilter(lookup_expr="icontains")
    status = filters.CharFilter(lookup_expr="icontains")
    diagnosing_clinician = filters.CharFilter(lookup_expr="icontains")

    # Date filters
    date_of_diagnosis = DateFilter()
    date_of_diagnosis_range = DateFromToRangeFilter()
    date_of_diagnosis_year = DateFilter(field_name="date_of_diagnosis", lookup_expr="year")
    date_of_diagnosis_month = DateFilter(field_name="date_of_diagnosis", lookup_expr="month")
    date_of_diagnosis_day = DateFilter(field_name="date_of_diagnosis", lookup_expr="day")

    class Meta:
        model = ClientDiagnosis
        fields = [
            "title",
            "diagnosis_code",
            "description",
            "severity",
            "status",
            "diagnosing_clinician",
            "date_of_diagnosis",
            "date_of_diagnosis_range",
            "date_of_diagnosis_year",
            "date_of_diagnosis_month",
            "date_of_diagnosis_day",
        ]


class ClientMedicationFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    dosage = filters.CharFilter(lookup_expr="icontains")
    frequency = filters.CharFilter(lookup_expr="icontains")
    start_date = filters.DateFilter()
    end_date = filters.DateFilter()
    notes = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ClientMedication
        fields = ["name", "dosage", "frequency", "start_date", "end_date", "notes"]


class ClientAllergyFilter(filters.FilterSet):
    allergy_type = filters.CharFilter(lookup_expr="icontains")
    severity = filters.CharFilter(lookup_expr="icontains")
    reaction = filters.CharFilter(lookup_expr="icontains")
    notes = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ClientAllergy
        fields = ["allergy_type", "severity", "reaction", "notes"]


class ClientDetailsFilter(filters.FilterSet):
    date_of_birth_range = DateFromToRangeFilter(field_name="date_of_birth")
    # status = CharFilter(method='filter_status')  # Use CharFilter with a custom method

    # def filter_status(self, queryset, name, value):
    #     if value:  # Proceed only if some value is provided
    #         # Split the value by commas and strip whitespace
    #         statuses = [status.strip() for status in value.split(',')]
    #         # Filter the queryset by these statuses
    #         queryset = queryset.filter(Q(status__in=statuses))
    #     return queryset

    class Meta:
        model = ClientDetails
        fields = {
            "first_name": ["exact", "icontains"],
            "last_name": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "organisation": ["exact", "icontains"],
            "location": ["exact"],
            "departement": ["exact", "icontains"],
            "gender": ["exact", "icontains"],
            "filenumber": ["exact", "gt", "lt"],
            "city": ["exact", "icontains"],
            "Zipcode": ["exact", "icontains"],
            "infix": ["exact", "icontains"],
            "streetname": ["exact", "icontains"],
            "street_number": ["exact", "icontains"],
            # 'date_of_birth': ['exact', 'year', 'month', 'day']
            "status": ["in"],  # Add this line to include the status field
        }


class InvoiceFilter(filters.FilterSet):
    invoice_number = filters.CharFilter(lookup_expr="icontains")
    client = filters.NumberFilter(field_name="client__id")
    issue_date = filters.DateFilter()
    due_date = filters.DateFilter()
    pre_vat_total = filters.NumberFilter()
    vat_rate = filters.NumberFilter()
    vat_amount = filters.NumberFilter()
    total_amount = filters.NumberFilter()
    status = filters.ChoiceFilter(choices=Invoice.Status.choices)
    payment_type = filters.ChoiceFilter(
        choices=Invoice.PaymentMethods.choices, null_label="Not Applicable/Not Paid"
    )  # New filter
    url = filters.CharFilter(lookup_expr="icontains")
    sender = filters.NumberFilter(field_name="client__sender")

    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "client",
            "issue_date",
            "due_date",
            "pre_vat_total",
            "vat_rate",
            "vat_amount",
            "total_amount",
            "status",
            "payment_type",
            "url",
        ]


class ContractFilterSchema(FilterSchema):
    sender: Optional[int] = None
    client: Optional[int] = None
    status: Optional[Literal["approved", "draft", "terminated", "stopped"]] = None
    type_id: Optional[int] = Field(None, q="type__id")
    price_frequency: Optional[Literal["minute", "hourly", "daily", "weekly", "monthly"]] = None
    care_type: Optional[Literal["ambulante", "accommodation"]] = None
    financing_act: Optional[Literal["WMO", "ZVW", "WLZ", "JW", "WPG"]] = None
    financing_option: Optional[Literal["ZIN", "PGB"]] = None


class DateFilterSchema(FilterSchema):
    start_date: Optional[datetime] = Field(None, q="date__gte")
    end_date: Optional[datetime] = Field(None, q="date__lte")


class InvoiceFilterSchema(FilterSchema):
    status: Optional[str] = Field(None)
    client: Optional[int] = Field(None)
    sender: Optional[int] = Field(None, q="client__sender__id")


class ClientStateFilter(FilterSchema):
    type: Optional[Literal["emotional", "physical"]] = None
