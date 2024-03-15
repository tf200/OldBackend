from django.urls import path
from .views import *

urlpatterns = [
    # ... other url patterns
    path('client_details/<int:pk>/', ClientDetailsView.as_view(), name='current-user'),
    path('client_update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('client_delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    path ('client_list/' , ClientListView.as_view() , name= 'clients_list'),
    path('client_create/' , ClientCreateView.as_view() , name = 'client_create'),



    path('diagnosis_create/' , DiagnosisCreateView.as_view() , name='diagnosis_create'),
    path('diagnosis_retreive/<int:pk>/' , DiagnosisRetrieveView.as_view() , name='diagnosis_retrieve'),
    path('diagnosis_list/<int:client>/' , DiagnosisListView.as_view() , name='diagnosis_list'),
    path('diagnosis_update/<int:pk>/' , DiagnosisUpdateView.as_view() , name='diagnosis_update'),
    path('diagnosis_delete/<int:pk>/' , DiagnosisDeleteView.as_view() , name='diagnosis_delete'),


    path('emergency_create/' , ClientEmergencyContactCreateView.as_view() , name='diagnosis_create'),
    path('emergency_retreive/<int:pk>/' , ClientEmergencyContactRetrieveView.as_view() , name='diagnosis_retrieve'),
    path('emergency_list/<int:client>/' , ClientEmergencyContactListView.as_view() , name='diagnosis_list'),
    path('emergency_update/<int:pk>/' , ClientEmergencyContactUpdateView.as_view() , name='diagnosis_update'),
    path('emergency_delete/<int:pk>/' , ClientEmergencyContactDeleteView.as_view() , name='diagnosis_delete'),


    path('document_upload/' , ClientDocumentsUploadView.as_view() , name= 'document_upload'),
    path('document_list/<int:client>/' , ClientDocumentsListView.as_view() , name = 'document_list'),
    path('document_delete/<int:pk>/', ClientDocumentsDeleteView.as_view() , name ='document_delete'),

    path('medication_create/' , ClientMedicationCreateView.as_view() , name='medication_create'),
    path('medication_retreive/<int:pk>/' , ClientMedicationRetrieveView.as_view() , name='medication_retrieve'),
    path('medication_list/<int:client>/' , ClientMedicationListView.as_view() , name='medication_list'),
    path('medication_update/<int:pk>/' , ClientMedicationUpdateView.as_view() , name='medication_update'),
    path('medication_delete/<int:pk>/' , ClientMedicationDeleteView.as_view() , name='medication_delete'),

    path('allergy_create/', ClientAllergyCreateView.as_view(), name='allergy_create'),
    path('allergy_retrieve/<int:pk>/', ClientAllergyRetrieveView.as_view(), name='allergy_retrieve'),
    path('allergy_list/<int:client>/', ClientAllergyListView.as_view(), name='allergy_list'),
    path('allergy_update/<int:pk>/', ClientAllergyUpdateView.as_view(), name='allergy_update'),
    path('allergy_delete/<int:pk>/', ClientAllergyDeleteView.as_view(), name='allergy_delete'),

    # path('progress_report/create/', ProgressReportCreateView.as_view(), name='progress_report_create'),
    # path('progress_report/retrieve/<int:pk>/', ProgressReportRetrieveView.as_view(), name='progress_report_retrieve'),
    # path('progress_report/list/<int:client>/', ProgressReportListView.as_view(), name='progress_report_list'),
    # path('progress_report/update/<int:pk>/', ProgressReportUpdateView.as_view(), name='progress_report_update'),
    # path('progress_report/delete/<int:pk>/', ProgressReportDeleteView.as_view(), name='progress_report_delete'),

    path('contract_create/', ContractCreateView.as_view(), name='contract_create'),
    path('contract_retrieve/<int:pk>/', ContractRetrieveView.as_view(), name='contract_retrieve'),
    path('contract_list/<int:client>/', ContractListView.as_view(), name='contract_list'),  
    path('contract_update/<int:pk>/', ContractUpdateView.as_view(), name='contract_update'),
    path('contract_delete/<int:pk>/', ContractDeleteView.as_view(), name='contract_delete'),


    path('sender_create/', ClientTypeCreateAPIView.as_view(), name='clienttype-create'),
    path('senders/', ClientTypeListView.as_view(), name='clienttype-list'),
    path('senders/<int:client_id>/', SenderRetrieveAPIView.as_view(), name='retrieve-sender'),


    
    path('temporary-files/', TemporaryFileUploadView.as_view(), name='temporary_file_upload'),
    path('generate-invoice/', GenerateInvoiceAPI.as_view(), name='generate-invoice'),
    path('invoices/<int:client_id>/', InvoiceListView.as_view(), name='invoice-list'),

    path('contract_all/', ContractListViewGeneral.as_view(), name='Contract-list'),
    path('invoice_all/', InvoiceListViewAll.as_view(), name='invoice-list-all'),
    path('invoice_ru/<int:pk>/', InvoiceRU.as_view(), name='invoice-list-all'),

]