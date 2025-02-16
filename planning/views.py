from django.shortcuts import get_object_or_404, render

# Create your views here.
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import CustomUser
from employees.models import EmployeeProfile
from planning.filters import AppointmentFilter

from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    AppointmentSerializerGet,
    AppointmentSerializerRUD,
    TemporaryFileSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AppointmentFilter

    def perform_update(self, serializer):
        employee_profile = get_object_or_404(EmployeeProfile, user=self.request.user)
        serializer.save(modified_by=employee_profile)


class AppointmentListView(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializerGet
    pagination_class = None
    filterset_class = AppointmentFilter


class AppointmentRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()


class TemporaryFileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TemporaryFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return the ID of the temporary file for later reference
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
