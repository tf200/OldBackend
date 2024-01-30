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
    
]