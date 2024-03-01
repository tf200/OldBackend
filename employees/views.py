from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from client.tasks import send_progress_report_email
from rest_framework.filters import OrderingFilter , SearchFilter
from client.pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import generics , status
from rest_framework.views import APIView
from django.shortcuts import render
from .serializers import *
from .models import *
from.filters import EmployeeProfileFilter
from django.db.utils import IntegrityError
from django.contrib.auth.models import Group
from adminmodif.permissions import IsMemberOfAuthorizedGroup
from django.shortcuts import get_object_or_404
from django.db.models import Q





class CurrentUserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = UserEmployeeProfileSerializer
    def get_object(self):
        # Assuming the EmployeeProfile model has a 'user' field that relates to the User model.
        queryset = EmployeeProfile.objects.all()  # Get the queryset of EmployeeProfile
        obj = get_object_or_404(queryset, user=self.request.user)  # Find the profile for the current user
        self.check_object_permissions(self.request, obj)  # Manually enforce permission checks
        return obj

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = UserEmployeeProfileSerializer
    queryset = EmployeeProfile.objects.all()

#=============================================================================


#=============================================================================
class ProgressReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientprogressSerializer
    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)
        # send_progress_report_email.delay(instance.id , instance.report_text) 

class ProgressReportRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()

class ProgressReportListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()

class ProgressReportDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()



#=====================================================
class ClientMeasurmentRUDView (generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = MeasurementSerializer
    queryset = Measurement.objects.all()


class ClientMeasurmentCLView (generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = MeasurementSerializer

class ClientMeasurmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ObservationsSerializer
    queryset = Observations.objects.all()

class ClientObservationsCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ObservationsSerializer

class ClientObservationsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)

class ClientFeedbackCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = FeedbackSerializer
    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)

class ClientFeedbackListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EmotionalStateSerializer
    queryset = EmotionalState.objects.all()

class ClientEmotionalStateCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EmotionalStateSerializer

class ClientEmotionalStateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = PhysicalStateSerializer
    queryset = PhysicalState.objects.all()

class ClientPhysicalStateCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = PhysicalStateSerializer

class ClientPhysicalStateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmployeeAssignmentSerializer
    queryset = ClientEmployeeAssignment.objects.all()

class ClientEmployeeAssignmentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmployeeAssignmentSerializer

class ClientEmployeeAssignmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientEmployeeAssignmentSerializer
#     queryset = ClientEmployeeAssignment.objects.all()

# class ClientEmployeeAssignmentCreateView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientEmployeeAssignmentSerializer


#=====================================================



class EmployeeProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EmployeeCRUDSerializer
    queryset = EmployeeProfile.objects.all()
    def get_serializer_context(self):
        context = super(EmployeeProfileRUDView, self).get_serializer_context()
        # Always include group details in the context for this view
        context['include_groups'] = True
        return context


class ProfilePictureAPIView(APIView):
    def get(self, request, employee_id):
        employee_profile = get_object_or_404(EmployeeProfile, pk=employee_id)
        user = employee_profile.user
        serializer = ProfilePictureSerializer(user)
        return Response(serializer.data)

    def patch(self, request, employee_id):
        employee_profile = get_object_or_404(EmployeeProfile, pk=employee_id)
        user = employee_profile.user
        serializer = ProfilePictureSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee_id):
        employee_profile = get_object_or_404(EmployeeProfile, pk=employee_id)
        user = employee_profile.user
        user.profile_picture.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)




class EmployeeProfileCreateView(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            employee_data = request.data

            first_name = employee_data.get('first_name', '')
            last_name = employee_data.get('last_name', '')
            username = generate_unique_username(first_name, last_name)
            password = make_password(None)

            user, user_created = CustomUser.objects.get_or_create(username=username)
            if user_created:
                user.set_password(password)
                user.save()
                default_group, group_created = Group.objects.get_or_create(name='Default')
                default_group.user_set.add(user)

            else:
                if hasattr(user, 'profile'):
                    return Response({"error": "This user already has an associated EmployeeProfile."},
                                    status=status.HTTP_400_BAD_REQUEST)

            try:
                employee_profile = EmployeeProfile.objects.create(user=user, **employee_data)
                serializer = EmployeeCRUDSerializer(employee_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




        
class EmployeeProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EmployeeCRUDSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = EmployeeProfileFilter  # Add SearchFilter here
    ordering_fields = ['-created']  # If you want to keep sorting functionality
    pagination_class = CustomPagination
    queryset = EmployeeProfile.objects.all()

    search_fields = [
        'first_name', 
        'last_name', 
        'position', 
        'department', 
        'employee_number', 
        'employment_number', 
        'private_email_address', 
        'email_address',
        'authentication_phone_number', 
        'private_phone_number', 
        'work_phone_number', 
        'home_telephone_number', 
        'gender'
    ]
    def get_queryset(self):
        queryset = super().get_queryset()
        group_name = self.request.query_params.get('groups')
        if group_name:
            # Correctly filter EmployeeProfile based on the group name through CustomUser
            queryset = queryset.filter(user__groupmembership__group__name=group_name
                                    ).distinct()
        return queryset
#================================================================

class CertificationRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = CertificationSerializer
    queryset = Certification.objects.all()


class CertificationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = CertificationSerializer


class CertificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = CertificationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        return Certification.objects.filter(employee=employee_id)  
#================================================================

class ExperienceRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

class ExperienceCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ExperienceSerializer

class ExperienceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ExperienceSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        return Experience.objects.filter(employee=employee_id)


#========================================================================

class ExperienceRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

class ExperienceCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ExperienceSerializer

class ExperienceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ExperienceSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        return Experience.objects.filter(employee=employee_id)
    


class EducationRUDView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EducationSerializer
    queryset = Education.objects.all()

class EducationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EducationSerializer


class EducationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = EducationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-end_date']  
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return Education.objects.filter(employee=employee_id)


    


