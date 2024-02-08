from .serializers import EmotionalStateSerializer, FeedbackSerializer, ObservationsSerializer, PhysicalStateSerializer, UserEmployeeProfileSerializer , ClientprogressSerializer , MeasurementSerializer
from .models import EmotionalState, Feedback, Observations, PhysicalState, ProgressReport , EmployeeProfile,Measurement
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from client.tasks import send_progress_report_email
from rest_framework.filters import OrderingFilter
from client.pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import render





class CurrentUserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserEmployeeProfileSerializer(request.user)
        return Response(serializer.data)



class ProgressReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)
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



#=====================================================
class ClientMeasurmentRUDView (generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer
    queryset = Measurement.objects.all()


class ClientMeasurmentCLView (generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer

class ClientMeasurmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_class = ProgressReportFilter  
    ordering_fields = ['date', 'client']
    ordering = ['date']
    pagination_class = CustomPagination  

    def get_queryset(self):
        client_id = self.kwargs['client']
        return Measurement.objects.filter(client=client_id)
    


#=====================================================
class ClientObservationsRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ObservationsSerializer
    queryset = Observations.objects.all()

class ClientObservationsCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ObservationsSerializer

class ClientObservationsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ObservationsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['client', 'date']
    ordering = ['date']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return Observations.objects.filter(client=client_id)
    


#=====================================================
class ClientFeedbackRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

class ClientFeedbackCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer

class ClientFeedbackListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['client', 'date']
    ordering = ['date']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return Feedback.objects.filter(client=client_id)
    


#=====================================================
class ClientEmotionalStateRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionalStateSerializer
    queryset = EmotionalState.objects.all()

class ClientEmotionalStateCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionalStateSerializer

class ClientEmotionalStateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionalStateSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['client', 'date']
    ordering = ['date']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return EmotionalState.objects.filter(client=client_id)    
    


#=====================================================
class ClientPhysicalStateRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhysicalStateSerializer
    queryset = PhysicalState.objects.all()

class ClientPhysicalStateCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhysicalStateSerializer

class ClientPhysicalStateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhysicalStateSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['client', 'date']
    ordering = ['date']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return PhysicalState.objects.filter(client=client_id)        