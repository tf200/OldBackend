from .models import EmotionalState, EmployeeProfile, Feedback, Observations, PhysicalState , ProgressReport , Measurement
from authentication.models import CustomUser
from rest_framework import serializers



class UserEmployeeProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture' , 'phone_number','profile' )
    
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
    class Meta :
        model = ProgressReport
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Measurement
        fields = '__all__'



class ObservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observations
        fields = '__all__'



class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'



class EmotionalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionalState
        fields = '__all__'



class PhysicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalState
        fields = '__all__'