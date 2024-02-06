from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from .models import *
from employees.serializers import UserEmployeeProfileSerializer
class MyCustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Call the superclass method to get a token
        token = super().get_token(user)

        # Add custom claims
        groups = user.groups.values_list('name', flat=True)
        token['groups'] = list(groups)  # Add group information to the token

        return token

    def validate(self, attrs):
        # Call the superclass's validate method to get the token pair
        data = super().validate(attrs)

        # Add user details to the response. Adjust this to include any information you need.
        user_data = UserEmployeeProfileSerializer(self.user).data  # Assuming you have this serializer defined elsewhere
        data.update({'user': user_data})

        return data



class CustomUserSerializer (serializers.ModelSerializer) :
    class Meta:
        model = CustomUser
        fields = ['username' , 'email' , 'first_name' , 'groups' , 'last_name']