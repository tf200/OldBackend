from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet , AppointmentListView , TemporaryFileUploadView



urlpatterns = [
    path('create/', AppointmentViewSet.as_view({
        'post': 'create',
    }), name='appointment-create'),
     path('list/', AppointmentListView.as_view(), name='appointment-list'),
     path('temporary-files/', TemporaryFileUploadView.as_view(), name='temporary_file_upload')

]