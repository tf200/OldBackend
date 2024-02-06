from rest_framework import serializers
from .models import *
from authentication.serializers import CustomUserSerializer



class ClientDetailsSerializer (serializers.ModelSerializer) :
    class Meta :
        model = ClientDetails
        fields = '__all__'

class ClientDetailsNestedSerializer (serializers.ModelSerializer) :
    class Meta :
        model = ClientDetails
        fields=['id','first_name' , 'last_name']



class ClientDiagnosisSerializer (serializers.ModelSerializer):
    client_details = ClientDetailsNestedSerializer(read_only = True)
    class Meta : 
        model = ClientDiagnosis
        fields = '__all__'



class ClientEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta : 
        model= ClientEmergencyContact
        fields = '__all__'




class ClientDocumentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ClientDocuments
        fields = '__all__'
        read_only_fields = ('uploaded_at', 'original_filename')  



class ClientMedicationSerializer(serializers.ModelSerializer) :
    class Meta :
        model= ClientMedication
        fields = '__all__'



class ClientAllergySerializer(serializers.ModelSerializer) :
    class Meta :
        model= ClientAllergy
        fields = '__all__'


# class ClientprogressSerializer(serializers.ModelSerializer):
#     class Meta :
#         model = ProgressReport
#         fields = '__all__'


class ContractSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Contract
        fields = '__all__'