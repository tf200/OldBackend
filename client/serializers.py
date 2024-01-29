from rest_framework import serializers
from .models import *
from authentication.serializers import CustomUserSerializer



class ClientDetailsSerializer (serializers.ModelSerializer) :
    class Meta :
        model = ClientDetails
        fields = '__all__'


