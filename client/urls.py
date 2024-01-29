from django.urls import path
from .views import ClientDetailsView , ClientListView , ClientCreateView

urlpatterns = [
    # ... other url patterns
    path('client_details/<int:pk>/', ClientDetailsView.as_view(), name='current-user'),
    path ('client_list/' , ClientListView.as_view() , name= 'clients_list'),
    path('client_create/' , ClientCreateView.as_view() , name = 'client_create')

]