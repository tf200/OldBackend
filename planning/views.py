from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions, viewsets , generics
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer , AppointmentSerializerGet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from authentication.models import CustomUser
from employees.models import EmployeeProfile

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Or any custom permission class

    def perform_create(self, serializer):
        # Assuming you have a way to get the EmployeeProfile from the request.user (JWT)
        employee_profile = get_object_or_404(EmployeeProfile, user=self.request.user)
        serializer.save(created_by=employee_profile)


class AppointmentListView(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializerGet