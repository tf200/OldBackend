from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from adminmodif.models import GroupMembership
from authentication.models import CustomUser

from .models import *


class UserEmployeeProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "profile_picture",
            "user",
            "position",
            "department",
            "email_address",
            "phone_number",
            "username",
        )

    def get_profile_picture(self, obj):
        if obj:
            user = obj.user  # Access the associated CustomUser instance
            if user.profile_picture:  # Check if profile_picture exists
                return user.profile_picture.url
        return None

    def get_username(self, obj):
        if obj:
            user = obj.user
            if user.username:
                return user.username
        return None

    def get_phone_number(self, obj):
        if obj:
            if obj.work_phone_number:
                return obj.work_phone_number
        return None


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["profile_picture"]


class ClientprogressSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = ProgressReport
        fields = "__all__"

    def get_full_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        else:
            return None

    def get_profile_picture(self, obj):
        if obj.author:
            return obj.author.user.profile_picture.url
        else:
            return None


class MeasurementSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    def get_client_name(self, obj):
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        else:
            return None

    class Meta:
        model = Measurement
        fields = ["client", "client_name", "date", "measurement_type", "value", "id"]


class ObservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observations
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        else:
            return None

    class Meta:
        model = Feedback
        fields = ["id", "author", "author_name", "client", "date", "feedback_text"]


class EmotionalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionalState
        fields = "__all__"


class PhysicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalState
        fields = "__all__"


class ClientEmployeeAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        else:
            return None

    class Meta:
        model = ClientEmployeeAssignment
        fields = ["client", "employee", "employee_name", "start_date", "role", "id"]


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name} {obj.user.profile_picture}"
        else:
            return None

    def get_location(self, obj):
        if obj.location:
            return obj.location.name
        else:
            return None

    class Meta:
        model = EmployeeProfile
        fields = [
            "user",
            "user_name",
            "position",
            "department",
            "highest_education",
            "university",
            "graduation_year",
            "certifications",
            "experience",
            "location",
            "has_borrowed",
            "out_of_service",
            "is_archived",
        ]


class EmployeeCRUDSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}}

    def get_profile_picture(self, obj):
        if obj:
            user = obj.user  # Access the associated CustomUser instance
            if user.profile_picture:  # Check if profile_picture exists
                return user.profile_picture.url
        return None

    def get_groups(self, obj):
        # Check if we should include group details
        if self.context.get("include_groups", False):
            memberships = GroupMembership.objects.filter(
                user=obj.user,
            ).select_related("group")

            return [
                {
                    "group_name": membership.group.name,
                    "start_date": membership.start_date,
                    "end_date": membership.end_date,
                }
                for membership in memberships
            ]
        else:
            # Do not include group details if the flag is not set
            return None


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class EmployeegetConv(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = "__all__"


class GoalsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalsReport
        fields = "__all__"


class ClientGoalsSerializer(serializers.ModelSerializer):
    goals_report = GoalsReportSerializer(read_only=True, many=True)

    class Meta:
        model = ClientGoals
        fields = "__all__"


class IncidentSerializer(serializers.ModelSerializer):
    involved_children_name = serializers.SerializerMethodField()
    reported_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Incident
        fields = "__all__"

    def get_involved_children_name(self, obj):
        if obj.involved_children:
            return [
                [f"{child.first_name} {child.last_name} " for child in obj.involved_children.all()]
            ]
        return []

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return f"{obj.reported_by.first_name} {obj.reported_by.last_name}"
        return None


class WeeklyReportSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReportSummary
        fields = "__all__"
