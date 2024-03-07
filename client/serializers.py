from rest_framework import serializers
from .models import *
from employees.models import ClientMedication 
from authentication.serializers import CustomUserSerializer
from django.db import transaction
from planning.serializers import move_file_s3


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
    name = serializers.SerializerMethodField()
    class Meta :
        model= ClientMedication
        fields = '__all__'
    def get_name(self, obj):
        if obj:
             # Access the associated CustomUser instance
            if obj.administered_by:  # Check if profile_picture exists
                return f'{obj.administered_by.first_name} {obj.administered_by.last_name}'
        return None



class ClientAllergySerializer(serializers.ModelSerializer) :
    class Meta :
        model= ClientAllergy
        fields = '__all__'


# class ClientprogressSerializer(serializers.ModelSerializer):
#     class Meta :
#         model = ProgressReport
#         fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    temporary_file_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    attachment_ids_to_delete = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Contract
        fields = ['sender', 'client', 'start_date', 'duration_client', 'duration_sender', 'care_type', 'rate_type', 'rate_value', 'temporary_file_ids', 'attachment_ids_to_delete']
        extra_kwargs = {
            'sender': {'required': True},
            'client': {'required': True}
        }

    def create(self, validated_data):
        with transaction.atomic():
            temporary_file_ids = validated_data.pop('temporary_file_ids', [])
            attachment_ids_to_delete = validated_data.pop('attachment_ids_to_delete', [])
            
            contract = Contract.objects.create(**validated_data)
            
            # Bulk delete specified attachments
            if attachment_ids_to_delete:
                ContractAttachment.objects.filter(id__in=attachment_ids_to_delete).delete()
            
            # Handle temporary files (attachments)
            temp_files = TemporaryFile.objects.filter(id__in=temporary_file_ids)
            attachments = []
            for temp_file in temp_files:
                # Assuming you have a similar file moving function as in your Appointment example
                old_key = temp_file.file.name
                new_key = f"contract_attachments/{old_key.split('/')[-1]}"
                
                # Implement your file moving logic here
                move_file_s3(old_key, new_key)
                
                attachments.append(ContractAttachment(
                    contract=contract,
                    attachment=f"{settings.MEDIA_URL}{new_key}",
                    name=temp_file.file.name.split('/')[-1]
                ))
                temp_file.delete()

            # Bulk create attachments
            ContractAttachment.objects.bulk_create(attachments)
            
            return contract
    def update(self, instance, validated_data):
        with transaction.atomic():
            # Pop attachment-related data that should not be directly updated in the Contract model
            temporary_file_ids = validated_data.pop('temporary_file_ids', [])
            attachment_ids_to_delete = validated_data.pop('attachment_ids_to_delete', [])
            
            # Update the Contract instance with other validated data
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Handle deletion of specified existing attachments
            if attachment_ids_to_delete:
                ContractAttachment.objects.filter(id__in=attachment_ids_to_delete).delete()

            # Process new temporary files as attachments
            if temporary_file_ids:
                temp_files = TemporaryFile.objects.filter(id__in=temporary_file_ids)
                attachments = []
                for temp_file in temp_files:
                    # Assuming you have a similar file moving function as in your Appointment example
                    old_key = temp_file.file.name
                    new_key = f"contract_attachments/{old_key.split('/')[-1]}"
                    
                    # Implement your file moving logic here
                    move_file_s3(old_key, new_key)
                    
                    attachments.append(ContractAttachment(
                        contract=instance,
                        attachment=f"{settings.MEDIA_URL}{new_key}",
                        name=temp_file.file.name.split('/')[-1]
                    ))
                    temp_file.delete()

                # Bulk create new attachments
                ContractAttachment.objects.bulk_create(attachments)

            return instance


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


class TemporaryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryFile
        fields = ['id', 'file']
