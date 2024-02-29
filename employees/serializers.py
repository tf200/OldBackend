from authentication.models import CustomUser
from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
from django.utils import timezone
from adminmodif.models import GroupMembership
from django.db.models import Q

class UserEmployeeProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = ( 'first_name', 'last_name','profile' , 'user')

    def get_profile(self, obj):
        if obj:
            user = obj.user  # Access the associated CustomUser instance
            if user.profile_picture:  # Check if profile_picture exists
                return user.profile_picture.url
        return None

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']


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
            return f"{obj.employee.first_name} {obj.employee.last_name}"
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
    profile_picture = serializers.SerializerMethodField()
    groups  = serializers.SerializerMethodField() 

    class Meta:
        model = EmployeeProfile
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def get_profile_picture(self, obj):
        if obj:
            user = obj.user  # Access the associated CustomUser instance
            if user.profile_picture:  # Check if profile_picture exists
                return user.profile_picture.url
        return None

    def get_groups(self, obj):
        # Check if we should include group details
        if self.context.get('include_groups', False):
            memberships = GroupMembership.objects.filter(
                user=obj.user,
            ).select_related('group')
            
            return [{
                'group_name': membership.group.name,
                'start_date': membership.start_date,
                'end_date': membership.end_date
            } for membership in memberships]
        else:
            # Do not include group details if the flag is not set
            return None



class CertificationSerializer (serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


class ExperienceSerializer (serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'
    

class EducationSerializer (serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'