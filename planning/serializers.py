from rest_framework import serializers
from .models import Appointment, AppointmentAttachment, EmployeeProfile, ClientDetails , TemporaryFile
import boto3
from django.conf import settings
from django.db import transaction

def move_file_s3(old_key, new_key):
        
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_S3_REGION_NAME)
        copy_source = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': old_key
        }
        # Copy the file to the new location
        s3.copy(copy_source, settings.AWS_STORAGE_BUCKET_NAME, new_key)
        # Delete the original file
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_key)


class AppointmentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentAttachment
        fields = ['file', 'name']

class AppointmentSerializer(serializers.ModelSerializer):
    temporary_file_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    

    class Meta:
        model = Appointment
        fields = ['title', 'description', 'appointment_type', 'start_time', 'end_time', 'employees', 'clients', 'location' , 'temporary_file_ids']
        extra_kwargs = {
            'employees': {'required': False},
            'clients': {'required': False},
        }



    def create(self, validated_data):
        print('hello')
        with transaction.atomic():
            

            temporary_file_ids = validated_data.pop('temporary_file_ids', [])
        
            employees_data = validated_data.pop('employees', [])
            clients_data = validated_data.pop('clients', [])

            appointment = Appointment.objects.create(**validated_data)

            if employees_data:
                appointment.employees.set(employees_data)
            if clients_data:
                appointment.clients.set(clients_data)

            for file_id in temporary_file_ids:
                temp_file = TemporaryFile.objects.get(id=file_id)
                # Determine new key for the file in the permanent storage
                old_key = temp_file.file.name
                new_key = f"appointment_attachments/{old_key.split('/')[-1]}"
               
                # Move the file on S3
                move_file_s3(old_key, new_key)
                
                # Create the AppointmentAttachment with the new file location
                AppointmentAttachment.objects.create(
                    appointment=appointment,
                    file=f"{settings.MEDIA_URL}{new_key}",  # Adjust based on your MEDIA_URL configuration
                    name=temp_file.file.name.split('/')[-1]
                )
                # Delete the TemporaryFile instance
                temp_file.delete()

            return appointment


class AppointmentSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__' 


class TemporaryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryFile
        fields = ['id', 'file']