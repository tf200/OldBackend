from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet



urlpatterns = [
    path('create/', AppointmentViewSet.as_view({
        'post': 'create',
    }), name='appointment-create'),
]