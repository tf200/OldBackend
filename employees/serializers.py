from authentication.models import CustomUser
from rest_framework import serializers
from .models import *


class UserEmployeeProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name',
                  'profile_picture', 'phone_number', 'profile')

    def get_profile(self, obj):
        try:
            profile = EmployeeProfile.objects.get(user=obj)
            return {
                "position": profile.position,
                "department": profile.department,
                "highest_education": profile.highest_education,
                "university": profile.university,
                "graduation_year": profile.graduation_year,
                "certifications": profile.certifications,
                "experience": profile.experience,
            }
        except EmployeeProfile.DoesNotExist:
            return None


class ClientprogressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressReport
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    def get_client_name(self, obj):
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        else:
            return None

    class Meta:
        model = Measurement
        fields = ['client', 'client_name', 'date', 'measurement_type', 'value']


class ObservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observations
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.user.first_name}  {obj.author.user.last_name}"
        else:
            return None

    class Meta:
        model = Feedback
        fields = ['id', 'author', 'author_name',
                  'client', 'date', 'feedback_text']


class EmotionalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionalState
        fields = '__all__'


class PhysicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalState
        fields = '__all__'


class ClientEmployeeAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.user.first_name} {obj.employee.user.last_name}"
        else:
            return None
        
    class Meta:
        model = ClientEmployeeAssignment
        fields = ['client', 'employee', 'employee_name', 'start_date', 'role']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name} {obj.user.profile_picture}"
        else:
            return None

    class Meta:
        model = EmployeeProfile
        fields = ['user', 'user_name', 'position', 'department', 'highest_education',
                  'university', 'graduation_year', 'certifications', 'experience']


class EmployeeCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}
