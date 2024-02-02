
from rest_framework import serializers
from .models import EmployeeProfile
from authentication.models import CustomUser



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