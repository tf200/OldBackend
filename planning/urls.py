from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet , AppointmentListView



urlpatterns = [
    path('create/', AppointmentViewSet.as_view({
        'post': 'create',
    }), name='appointment-create'),
     path('list/', AppointmentListView.as_view(), name='appointment-list'),
]