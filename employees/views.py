from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from client.tasks import send_progress_report_email
from rest_framework.filters import OrderingFilter
from client.pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import generics , status
from rest_framework.views import APIView
from django.shortcuts import render
from .serializers import *
from .models import *
from django.db.utils import IntegrityError





class CurrentUserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserEmployeeProfileSerializer(request.user)
        return Response(serializer.data)
#=============================================================================


#=============================================================================
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
    ordering = ['-created']
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
    ordering = ['-created']
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
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return Observations.objects.filter(client=client_id)
    


#=====================================================
class ClientFeedbackRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)

class ClientFeedbackCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)

class ClientFeedbackListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['client', 'date']
    ordering = ['-created']
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
    ordering = ['-created']
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
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return PhysicalState.objects.filter(client=client_id)        



#=====================================================
class ClientEmployeeAssignmentRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmployeeAssignmentSerializer
    queryset = ClientEmployeeAssignment.objects.all()

class ClientEmployeeAssignmentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmployeeAssignmentSerializer

class ClientEmployeeAssignmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmployeeAssignmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['client', 'start_date']
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientEmployeeAssignment.objects.filter(client=client_id)        



#=====================================================
# class ClientEmployeeAssignmentRUDView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ClientEmployeeAssignmentSerializer
#     queryset = ClientEmployeeAssignment.objects.all()

# class ClientEmployeeAssignmentCreateView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ClientEmployeeAssignmentSerializer


#=====================================================



class EmployeeProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeCRUDSerializer
    queryset = EmployeeProfile.objects.all()


class EmployeeProfileCreateView(APIView):
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            employee_data = request.data

            first_name = employee_data.get('first_name', '')
            last_name = employee_data.get('last_name', '')
            username = generate_unique_username(first_name, last_name)
            print(username)
            password = make_password(None)  

            
            user, user_created = CustomUser.objects.get_or_create(username=username)
            if user_created:
                user.set_password(password)
                user.save()
        
            else:
                
                if hasattr(user, 'profile'):
                
                    return Response({"error": "This user already has an associated EmployeeProfile."},
                                    status=status.HTTP_400_BAD_REQUEST)

        
            try:
                employee_profile = EmployeeProfile.objects.create(user=user, **employee_data)
                print(employee_profile.id)
                serializer = EmployeeCRUDSerializer(employee_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                 
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class EmployeeProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeCRUDSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    #ordering_fields = ['client', 'start_date']
    ordering = ['-created']
    pagination_class = CustomPagination
    queryset = EmployeeProfile.objects.all()
 