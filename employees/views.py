import string

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from adminmodif.permissions import IsMemberOfAuthorizedGroup, IsMemberOfManagement
from client.pagination import CustomPagination
from client.tasks import send_progress_report_email

from .filters import EmployeeProfileFilter
from .models import *
from .serializers import *
from .tasks import send_login_credentials, summarize_weekly_reports
from .utils import generate_unique_username


class CurrentUserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmployeeProfileSerializer

    def get_object(self):
        # Assuming the EmployeeProfile model has a 'user' field that relates to the User model.
        queryset = EmployeeProfile.objects.all()  # Get the queryset of EmployeeProfile
        obj = get_object_or_404(
            queryset, user=self.request.user
        )  # Find the profile for the current user
        self.check_object_permissions(self.request, obj)  # Manually enforce permission checks
        return obj


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmployeeProfileSerializer
    queryset = EmployeeProfile.objects.all()


# =============================================================================


# =============================================================================
class ProgressReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer

    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)
        # send_progress_report_email.delay(instance.id , instance.report_text)


class ProgressReportRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()


class ProgressReportListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientprogressSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_class = ProgressReportFilter
    ordering_fields = ["date", "client"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return ProgressReport.objects.filter(client=client_id)


class ProgressReportUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()


class ProgressReportDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientprogressSerializer
    queryset = ProgressReport.objects.all()


# =====================================================
class ClientMeasurmentRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeasurementSerializer
    queryset = Measurement.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ClientMeasurmentCLView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeasurementSerializer


class ClientMeasurmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = MeasurementSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_class = ProgressReportFilter
    ordering_fields = ["date", "client"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return Measurement.objects.filter(client=client_id)


# =====================================================
class ClientObservationsRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ObservationsSerializer
    queryset = Observations.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ClientObservationsCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ObservationsSerializer


class ClientObservationsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ObservationsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["client", "date"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return Observations.objects.filter(client=client_id)


# =====================================================
class ClientFeedbackRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ClientFeedbackCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(author=employee_profile)


class ClientFeedbackListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = FeedbackSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["client", "date"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return Feedback.objects.filter(client=client_id)


# =====================================================
class ClientEmotionalStateRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmotionalStateSerializer
    queryset = EmotionalState.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ClientEmotionalStateCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionalStateSerializer


class ClientEmotionalStateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = EmotionalStateSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["client", "date"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return EmotionalState.objects.filter(client=client_id)


# =====================================================
class ClientPhysicalStateRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PhysicalStateSerializer
    queryset = PhysicalState.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ClientPhysicalStateCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhysicalStateSerializer


class ClientPhysicalStateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = PhysicalStateSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["client", "date"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return PhysicalState.objects.filter(client=client_id)


# =====================================================
class ClientEmployeeAssignmentRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientEmployeeAssignmentSerializer
    queryset = ClientEmployeeAssignment.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ClientEmployeeAssignmentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmployeeAssignmentSerializer


class ClientEmployeeAssignmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientEmployeeAssignmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["client", "start_date"]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs["client"]
        return ClientEmployeeAssignment.objects.filter(client=client_id)


# =====================================================
# class ClientEmployeeAssignmentRUDView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientEmployeeAssignmentSerializer
#     queryset = ClientEmployeeAssignment.objects.all()

# class ClientEmployeeAssignmentCreateView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientEmployeeAssignmentSerializer


# =====================================================


class EmployeeProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeCRUDSerializer
    queryset = EmployeeProfile.objects.all()

    def get_serializer_context(self):
        context = super(EmployeeProfileRUDView, self).get_serializer_context()
        # Always include group details in the context for this view
        context["include_groups"] = True
        return context

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ProfilePictureAPIView(APIView):
    permission_classes = [IsAuthenticated]

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


def generate_random_password(length=12):
    """
    Generate a random password with the specified length.
    Includes uppercase and lowercase letters, digits, and symbols.
    """
    # Define the characters to use in the password
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"

    # Ensure the password is random and meets the requirements
    password = get_random_string(length, characters)

    return password


class EmployeeProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            employee_data = request.data

            first_name = employee_data.get("first_name", "")
            last_name = employee_data.get("last_name", "")
            email = employee_data.get("private_email_address", "")
            username = generate_unique_username(first_name, last_name)

            # Generate a plain text password
            plain_text_password = (
                generate_random_password()
            )  # Implement this function to generate a secure password

            user, user_created = CustomUser.objects.get_or_create(username=username)
            if user_created:
                # Hash the password after it's been used to send in email
                user.set_password(plain_text_password)
                user.save()

                # Now, send the plain text password via email
                send_login_credentials.delay(email, username, plain_text_password)

                default_group, group_created = Group.objects.get_or_create(name="Default")
                default_group.user_set.add(user)
            else:
                if hasattr(user, "profile"):
                    return Response(
                        {"error": "This user already has an associated EmployeeProfile."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            try:
                employee_profile = EmployeeProfile.objects.create(user=user, **employee_data)
                serializer = EmployeeCRUDSerializer(employee_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = EmployeeCRUDSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = EmployeeProfileFilter  # Add SearchFilter here
    ordering_fields = ["-created"]  # If you want to keep sorting functionality
    pagination_class = CustomPagination
    queryset = EmployeeProfile.objects.all()

    search_fields = [
        "first_name",
        "last_name",
        "position",
        "department",
        "employee_number",
        "employment_number",
        "private_email_address",
        "email_address",
        "authentication_phone_number",
        "private_phone_number",
        "work_phone_number",
        "home_telephone_number",
        "gender",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        group_name = self.request.query_params.get("groups")
        if group_name:
            # Correctly filter EmployeeProfile based on the group name through CustomUser
            queryset = queryset.filter(user__groupmembership__group__name=group_name).distinct()
        return queryset


# ================================================================


class CertificationRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CertificationSerializer
    queryset = Certification.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class CertificationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CertificationSerializer


class CertificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = CertificationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs["employee_id"]
        return Certification.objects.filter(employee=employee_id)


# ================================================================


class ExperienceRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ExperienceCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExperienceSerializer


class ExperienceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ExperienceSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs["employee_id"]
        return Experience.objects.filter(employee=employee_id)


# ========================================================================


class ExperienceRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class ExperienceCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExperienceSerializer


class ExperienceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ExperienceSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["-created"]
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs["employee_id"]
        return Experience.objects.filter(employee=employee_id)


class EducationRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EducationSerializer
    queryset = Education.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class EducationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EducationSerializer


class EducationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = EducationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["-end_date"]
    pagination_class = CustomPagination

    def get_queryset(self):
        employee_id = self.kwargs.get("employee_id")
        return Education.objects.filter(employee=employee_id)


class EmployeeProfileRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeegetConv
    lookup_field = "user__id"

    def get_object(self):
        """
        Overrides the standard `get_object` method to return the profile
        based on the user's id passed in the URL.
        """
        user_id = self.kwargs.get("user__id")
        return get_object_or_404(EmployeeProfile, user__id=user_id)


class ClientGoalsCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientGoalsSerializer

    def perform_create(self, serializer):
        user = self.request.user
        employee_profile = EmployeeProfile.objects.get(user=user)
        serializer.save(administered_by=employee_profile)


class ClientGoalsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientGoalsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        This view should return a list of all the client goals
        for the client as determined by the client_id portion of the URL.
        """
        client_id = self.kwargs["client_id"]
        return ClientGoals.objects.filter(client=client_id)


class ClientGoalDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClientGoals.objects.all()
    serializer_class = ClientGoalsSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class GoalsReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GoalsReportSerializer


class GoalsReportRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalsReportSerializer
    queryset = GoalsReport.objects.all()

    def get_permissions(self):
        if self.request.method in ["GET"]:
            permission_classes = [IsAuthenticated, IsMemberOfManagement]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]  # Default permission class(es)
        return [permission() for permission in permission_classes]


class IncidentListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = IncidentSerializer


class IncidentByChildAPIView(generics.ListAPIView):  # Using ListAPIView for listing
    serializer_class = IncidentSerializer

    def get_queryset(self):
        """
        This view returns a list of all incidents for a specific child
        by filtering against a `child_id` in the URL.
        """
        child_id = self.kwargs.get("child_id")
        return Incident.objects.filter(involved_children__id=child_id)


class IncidentRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    lookup_field = "id"


class WeeklyReportSummaryRUD(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = WeeklyReportSummarySerializer
    queryset = WeeklyReportSummary.objects.all()


class WeeklyReportSummaryCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = WeeklyReportSummarySerializer


class WeeklyReportSummaryListAll(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = WeeklyReportSummarySerializer
    queryset = WeeklyReportSummary.objects.all()


@api_view(["GET"])
def generate_ai_reports(req):
    summarize_weekly_reports()
    return Response({"status": "success", "message": "finished successfully"})
