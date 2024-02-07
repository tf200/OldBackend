from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from .models import *
from employees.serializers import UserEmployeeProfileSerializer
class MyCustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        
        token = super().get_token(user)

        # Add custom claims
        groups = user.groups.values_list('name', flat=True)
        token['groups'] = list(groups)  

        return token

    def validate(self, attrs):
       
        data = super().validate(attrs)

        
        user_data = UserEmployeeProfileSerializer(self.user).data  
        data.update({'user': user_data})

        return data



class CustomUserSerializer (serializers.ModelSerializer) :
    class Meta:
        model = CustomUser
        fields = ['username' , 'email' , 'first_name' , 'groups' , 'last_name']