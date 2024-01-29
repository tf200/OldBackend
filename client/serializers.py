from rest_framework import serializers
from .models import *
from authentication.serializers import CustomUserSerializer



class ClientDetailsSerializer (serializers.ModelSerializer) :
    user = CustomUserSerializer(read_only = True)
    class Meta :
        model = ClientDetails
        fields = '__all__'


