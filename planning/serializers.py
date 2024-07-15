import boto3
from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from .models import (
    Appointment,
    AppointmentAttachment,
    ClientDetails,
    EmployeeProfile,
    TemporaryFile,
)


def move_file_s3(old_key, new_key):

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    copy_source = {"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": old_key}
    # Copy the file to the new location
    s3.copy(copy_source, settings.AWS_STORAGE_BUCKET_NAME, new_key)
    # Delete the original file
    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_key)


class AppointmentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentAttachment
        fields = ["id", "file", "name"]


class AppointmentSerializer(serializers.ModelSerializer):
    # temporary_file_ids = serializers.ListField(
    #     child=serializers.UUIDField(), write_only=True, required=False
    # )
    attachment_ids_to_delete = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_null=True
    )
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "title",
            "description",
            "appointment_type",
            "start_time",
            "end_time",
            "employees",
            "clients",
            "location",
            "temporary_file_ids",
            "attachment_ids_to_delete",
            "attachments",
        ]
        extra_kwargs = {
            "employees": {"required": False},
            "clients": {"required": False},
            "attachment_ids_to_delete": {"required": False},
            "id": {"read_only": True},
        }

    def get_attachments(self, obj: Appointment):
        return obj.get_attachments()

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["attachments"] = ["ssss"]
    #     return data

    def create(self, validated_data):
        with transaction.atomic():
            # temporary_file_ids = validated_data.pop("temporary_file_ids", [])
            # attachment_ids_to_delete = validated_data.pop("attachment_ids_to_delete", [])
            employees_data = validated_data.pop("employees", [])
            clients_data = validated_data.pop("clients", [])

            appointment = Appointment.objects.create(**validated_data)

            if employees_data:
                appointment.employees.set(employees_data)
            if clients_data:
                appointment.clients.set(clients_data)

            # Bulk delete specified attachments
            # if attachment_ids_to_delete:
            #     AppointmentAttachment.objects.filter(id__in=attachment_ids_to_delete).delete()

            # Fetch all TemporaryFiles in one go
            # temp_files = TemporaryFile.objects.filter(id__in=temporary_file_ids)
            # attachments = []

            # for temp_file in temp_files:
            #     old_key = temp_file.file.name
            #     new_key = f"appointment_attachments/{old_key.split('/')[-1]}"

            #     move_file_s3(old_key, new_key)

            #     attachments.append(
            #         AppointmentAttachment(
            #             appointment=appointment,
            #             file=f"{settings.MEDIA_URL}{new_key}",
            #             name=temp_file.file.name.split("/")[-1],
            #         )
            #     )

            #     temp_file.delete()

            # Bulk create attachments
            # AppointmentAttachment.objects.bulk_create(attachments)

            return appointment

    def update(self, instance, validated_data):
        with transaction.atomic():
            # temporary_file_ids = validated_data.pop("temporary_file_ids", [])
            # attachment_ids_to_delete = validated_data.pop("attachment_ids_to_delete", [])
            employees_data = validated_data.pop("employees", None)
            clients_data = validated_data.pop("clients", None)

            # Update instance fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update ManyToMany fields (employees and clients)
            if employees_data is not None:
                instance.employees.set(employees_data)
            if clients_data is not None:
                instance.clients.set(clients_data)

            # Handle temporary file attachments
            # for file_id in temporary_file_ids:
            #     temp_file = TemporaryFile.objects.get(id=file_id)
            #     old_key = temp_file.file.name
            #     new_key = f"appointment_attachments/{old_key.split('/')[-1]}"
            #     move_file_s3(old_key, new_key)
            #     AppointmentAttachment.objects.create(
            #         appointment=instance,
            #         file=f"{settings.MEDIA_URL}{new_key}",
            #         name=temp_file.file.name.split("/")[-1],
            #     )
            #     temp_file.delete()

            # Delete specified attachments
            # if attachment_ids_to_delete:
            #     AppointmentAttachment.objects.filter(id__in=attachment_ids_to_delete).delete()

            return instance


class AppointmentSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"


class AppointmentSerializerRUD(serializers.ModelSerializer):
    attachments = AppointmentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"


class TemporaryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryFile
        fields = ["id", "file"]
