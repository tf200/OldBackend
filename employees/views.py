from django.shortcuts import render

# Create your views here.


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserEmployeeProfileSerializer , ClientprogressSerializer
from rest_framework.response import Response
from client.tasks import send_progress_report_email
from .models import ProgressReport
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from client.pagination import CustomPagination





class CurrentUserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserEmployeeProfileSerializer(request.user)
        return Response(serializer.data)




class ProgressReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author) 
        # send_progress_report_email.delay(instance.id , instance.report_text) 

class ProgressReportRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()

class ProgressReportListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_class = ProgressReportFilter  
    ordering_fields = ['date', 'client']
    ordering = ['date']
    pagination_class = CustomPagination  

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ProgressReport.objects.filter(client=client_id)

class ProgressReportUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()

class ProgressReportDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()