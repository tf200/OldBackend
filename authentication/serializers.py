from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from .models import *
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        groups = user.groups.values_list('name', flat=True)
        # Add custom claims
        token['group'] = list(groups)
        # ...

        return token



class CustomUserSerializer (serializers.ModelSerializer) :
    class Meta:
        model = CustomUser
        fields = ['username' , 'email' , 'first_name' , 'groups' , 'last_name']