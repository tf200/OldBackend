from rest_framework import serializers
from .models import Appointment, AppointmentAttachment, EmployeeProfile, ClientDetails

class AppointmentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentAttachment
        fields = ['file', 'name']

class AppointmentSerializer(serializers.ModelSerializer):
    attachments = AppointmentAttachmentSerializer(many=True, required=False)

    class Meta:
        model = Appointment
        fields = ['title', 'description', 'appointment_type', 'start_time', 'end_time', 'employees', 'clients', 'location', 'attachments']
        extra_kwargs = {
            'employees': {'required': False},
            'clients': {'required': False},
        }

    def create(self, validated_data):
        attachments_data = validated_data.pop('attachments', [])
        employees_data = validated_data.pop('employees', [])  # Extract employees data
        clients_data = validated_data.pop('clients', [])  # Extract clients data

        # Create the Appointment instance
        appointment = Appointment.objects.create(**validated_data)

        # Handle the ManyToMany fields
        if employees_data:
            appointment.employees.set(employees_data)  # Assuming employees_data contains employee instances or IDs
        if clients_data:
            appointment.clients.set(clients_data)  # Assuming clients_data contains client instances or IDs

        # Handle attachments
        for attachment_data in attachments_data:
            AppointmentAttachment.objects.create(appointment=appointment, **attachment_data)

        return appointment


class AppointmentSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__' 