from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import *
from adminmodif.models import GroupMembership



class MyCustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Fetch groups for the user
        # Since the background worker manages the active status, 
        # we can directly fetch the groups without filtering on dates.
        groups = GroupMembership.objects.filter(user=user).values_list('group__name', flat=True)
        token['groups'] = list(groups)

        return token


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CustomUserSerializer (serializers.ModelSerializer) :
    class Meta:
        model = CustomUser
        fields = ['username' , 'email' , 'first_name' , 'groups' , 'last_name']