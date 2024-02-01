from rest_framework import serializers
from .models import *
from authentication.serializers import CustomUserSerializer



class ClientDetailsSerializer (serializers.ModelSerializer) :
    class Meta :
        model = ClientDetails
        fields = '__all__'


class ClientDiagnosisSerializer (serializers.ModelSerializer):
    class Meta : 
        model = ClientDiagnosis
        fields = '__all__'



class ClientEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta : 
        model= ClientEmergencyContact
        fields = '__all__'




class ClientDocumentsSerializers(serializers.ModelSerializer) :
    class Meta :
        model= ClientDocuments
        fields = '__all__'