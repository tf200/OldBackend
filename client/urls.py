from django.urls import path
from .views import *

urlpatterns = [
    # ... other url patterns
    path('client_details/<int:pk>/', ClientDetailsView.as_view(), name='current-user'),
    path ('client_list/' , ClientListView.as_view() , name= 'clients_list'),
    path('client_create/' , ClientCreateView.as_view() , name = 'client_create'),
    path('diagnosis_create/' , DiagnosisCreateView.as_view() , name='diagnosis_create'),
    path('diagnosis_retreive/<int:pk>/' , DiagnosisRetrieveView.as_view() , name='diagnosis_retrieve'),
    path('diagnosis_list/<int:client>/' , DiagnosisListView.as_view() , name='diagnosis_list')
    

]