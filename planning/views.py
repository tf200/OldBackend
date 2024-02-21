from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions, viewsets , generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Appointment
from .serializers import AppointmentSerializer , AppointmentSerializerGet , TemporaryFileSerializer
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
    pagination_class = None



class TemporaryFileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TemporaryFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return the ID of the temporary file for later reference
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)