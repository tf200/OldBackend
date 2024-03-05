from rest_framework import serializers
from .models import *
from employees.models import ClientMedication
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


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'phone_number', 'email']

class ClientTypeSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, required=False)  # Set `required=False` if contacts are optional

    class Meta:
        model = ClientType
        fields = ['id','types', 'name', 'address', 'postal_code', 'place', 'land', 'KVKnumber', 'BTWnumber', 'phone_number', 'client_number', 'contacts']

    def create(self, validated_data):
        contacts_data = validated_data.pop('contacts', [])  # Safely remove contacts with a default empty list
        client_type = ClientType.objects.create(**validated_data)
        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(**contact_data)
            ClientTypeContactRelation.objects.create(client_type=client_type, contact=contact)
        return client_type

    def get_contacts(self, obj):
        # Assuming 'contact_relations' is the related_name for the ForeignKey in ClientTypeContactRelation
        contacts = [relation.contact for relation in obj.contact_relations.all()]
        return ContactSerializer(contacts, many=True).data






