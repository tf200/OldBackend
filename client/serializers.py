import json

from django.db import transaction
from rest_framework import serializers

from authentication.serializers import CustomUserSerializer
from employees.models import ClientMedication
from planning.serializers import move_file_s3
from system.models import AttachmentFile
from system.serializers import AttchementFileSerialize

from .models import *


class ClientDetailsSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    document_info = serializers.SerializerMethodField()

    class Meta:
        model = ClientDetails
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "date_of_birth",
            "identity",
            "status",
            "bsn",
            "source",
            "birthplace",
            "email",
            "phone_number",
            "organisation",
            "departement",
            "gender",
            "filenumber",
            "profile_picture",
            "city",
            "Zipcode",
            "infix",
            "streetname",
            "street_number",
            "created",
            "sender",
            "location",
            "attachments",
            "identity_attachment_ids",
            "departure_reason",
            "departure_report",
            "gps_position",
            "document_info",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "profile_picture": {"required": False},
            "gps_position": {"read_only": True},
        }

    def get_location(self, obj):
        if obj.location:
            return obj.location.name
        return None

    def to_representation(self, instance: ClientDetails):
        representation = super().to_representation(instance)
        representation["has_untaken_medications"] = instance.has_untaken_medications()
        return representation

    def get_attachments(self, obj: ClientDetails):
        attachment_ids = obj.identity_attachment_ids
        attachments = AttachmentFile.objects.filter(id__in=attachment_ids, is_used=True)
        return AttchementFileSerialize(attachments, many=True).data

    def get_document_info(self, obj: ClientDetails):
        return obj.documents_info()


class ClientDetailsNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDetails
        fields = ["id", "first_name", "last_name"]


class ClientDiagnosisSerializer(serializers.ModelSerializer):
    client_details = ClientDetailsNestedSerializer(read_only=True)

    class Meta:
        model = ClientDiagnosis
        fields = "__all__"


class ClientEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientEmergencyContact
        fields = "__all__"
        read_only_fields = ("uuid",)


class ClientDocumentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ClientDocuments
        fields = "__all__"
        read_only_fields = ("uploaded_at", "original_filename")


class ClientMedicationSerializer(serializers.ModelSerializer):
    administer_name = serializers.SerializerMethodField()

    class Meta:
        model = ClientMedication
        fields = "__all__"

    def get_administer_name(self, obj):
        if obj:
            # Access the associated CustomUser instance
            if obj.administered_by:  # Check if profile_picture exists
                return f"{obj.administered_by.first_name} {obj.administered_by.last_name}"
        return None


class ClientAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAllergy
        fields = "__all__"


# class ClientprogressSerializer(serializers.ModelSerializer):
#     class Meta :
#         model = ProgressReport
#         fields = '__all__'
class ContractAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAttachment
        fields = ["id", "contract", "name", "attachment", "created_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["attachment"] = instance.attachment.url if instance.attachment else None
        return representation


class ContractSerializer(serializers.ModelSerializer):
    attachments = ContractAttachmentSerializer(many=True, required=False, read_only=True)
    temporary_file_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    attachment_ids_to_delete = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Contract
        fields = [
            "id",
            "sender",
            "client",
            "start_date",
            "duration_client",
            "duration_sender",
            "care_type",
            "rate_type",
            "rate_value",
            "temporary_file_ids",
            "attachment_ids_to_delete",
            "attachments",
            "contract_type",
        ]
        extra_kwargs = {"sender": {"required": True}, "client": {"required": True}}

    def create(self, validated_data):
        with transaction.atomic():
            temporary_file_ids = validated_data.pop("temporary_file_ids", [])
            attachment_ids_to_delete = validated_data.pop("attachment_ids_to_delete", [])

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

                attachments.append(
                    ContractAttachment(
                        contract=contract,
                        attachment=f"{settings.MEDIA_URL}{new_key}",
                        name=temp_file.file.name.split("/")[-1],
                    )
                )
                temp_file.delete()

            # Bulk create attachments
            ContractAttachment.objects.bulk_create(attachments)

            return contract

    def update(self, instance, validated_data):
        with transaction.atomic():
            # Pop attachment-related data that should not be directly updated in the Contract model
            temporary_file_ids = validated_data.pop("temporary_file_ids", [])
            attachment_ids_to_delete = validated_data.pop("attachment_ids_to_delete", [])

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

                    attachments.append(
                        ContractAttachment(
                            contract=instance,
                            attachment=f"{settings.MEDIA_URL}{new_key}",
                            name=temp_file.file.name.split("/")[-1],
                        )
                    )
                    temp_file.delete()

                # Bulk create new attachments
                ContractAttachment.objects.bulk_create(attachments)

            return instance


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["name", "phone_number", "email"]


class ClientTypeSerializer(serializers.ModelSerializer):

    contacts = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = ClientType
        fields = [
            "id",
            "types",
            "name",
            "address",
            "postal_code",
            "place",
            "land",
            "KVKnumber",
            "BTWnumber",
            "phone_number",
            "client_number",
            "contacts",
        ]

    def create(self, validated_data):
        contacts_data = validated_data.pop(
            "contacts", []
        )  # Safely remove contacts with a default empty list

        client_type = ClientType.objects.create(**validated_data)

        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(**contact_data)
            ClientTypeContactRelation.objects.create(client_type=client_type, contact=contact)

        return client_type

    def update(self, instance: ClientType, validated_data):
        contacts_data = validated_data.pop("contacts", [])

        # Update the ClientType instance with other validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create contacts
        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(**contact_data)
            ClientTypeContactRelation.objects.get_or_create(client_type=instance, contact=contact)

        return instance

    def to_representation(self, instance: ClientType):
        data = super().to_representation(instance)
        data["contacts"] = ContactSerializer(instance.get_contacts(), many=True).data
        return data

    # def get_contacts(self, obj: ClientType):
    #     # List all the Contacts instances related to the ClientType instance
    #     contacts = obj.get_contacts()

    #     return ContactSerializer(contacts, many=True).data


class TemporaryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryFile
        fields = ["id", "file"]


class InvoiceContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceContract
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = [
            "invoice_number",
            "issue_date",
            "pre_vat_total",
            "vat_rate",
            "vat_amount",
            "total_amount",
        ]

    def get_full_name(self, obj):
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        else:
            return None

    def get_sender(self, obj) -> str | None:
        if obj.client:
            return obj.client.sender.name if obj.client.sender is not None else None
        else:
            return None


class CareplanAtachementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareplanAtachements
        fields = "__all__"


class CarePlanSerializer(serializers.ModelSerializer):
    attachments = CareplanAtachementsSerializer(
        many=True, required=False, read_only=True, source="care_attachement"
    )
    temporary_file_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    attachment_ids_to_delete = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_null=True
    )
    domain_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_null=True, default=list
    )

    class Meta:
        model = CarePlan
        fields = [
            "id",
            "client",
            "start_date",
            "end_date",
            "description",
            "status",
            "temporary_file_ids",
            "attachment_ids_to_delete",
            "attachments",
            "domain_ids",
        ]
        extra_kwargs = {"client": {"required": True}}

    def to_representation(self, instance: CarePlan):
        ret = super().to_representation(instance)
        ret["domain_ids"] = [domain.id for domain in instance.domains.all()]
        return ret

    def create(self, validated_data):
        with transaction.atomic():
            temporary_file_ids = validated_data.pop("temporary_file_ids", [])
            attachment_ids_to_delete = validated_data.pop("attachment_ids_to_delete", [])
            domain_ids: list[int] = validated_data.pop("domain_ids", [])

            careplan = CarePlan.objects.create(**validated_data)

            # register domains
            for domain_id in domain_ids:
                try:
                    domain = AssessmentDomain.objects.get(id=domain_id)
                    careplan.domains.add(domain)
                except AssessmentDomain.DoesNotExist:
                    pass

            # Bulk delete specified attachments
            if attachment_ids_to_delete:
                CareplanAtachements.objects.filter(id__in=attachment_ids_to_delete).delete()

            # Handle temporary files (attachments)
            temp_files = TemporaryFile.objects.filter(id__in=temporary_file_ids)
            attachments = []
            for temp_file in temp_files:
                # Assuming you have a similar file moving function as in your Appointment example
                old_key = temp_file.file.name
                new_key = f"clients_pics/{old_key.split('/')[-1]}"

                # Implement your file moving logic here
                move_file_s3(old_key, new_key)

                attachments.append(
                    CareplanAtachements(
                        careplan=careplan,
                        attachement=f"{settings.MEDIA_URL}{new_key}",
                        name=temp_file.file.name.split("/")[-1],
                    )
                )
                temp_file.delete()

            # Bulk create attachments
            CareplanAtachements.objects.bulk_create(attachments)

            return careplan

    def update(self, instance: CarePlan, validated_data):
        with transaction.atomic():
            # Pop attachment-related data that should not be directly updated in the Contract model
            temporary_file_ids = validated_data.pop("temporary_file_ids", [])
            attachment_ids_to_delete = validated_data.pop("attachment_ids_to_delete", [])
            domain_ids: list[int] = validated_data.pop("domain_ids", [])

            # Update the Contract instance with other validated data
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Delete all previous domains
            if domain_ids:
                instance.domains.clear()

            # register the new domains
            for domain_id in domain_ids:
                try:
                    domain = AssessmentDomain.objects.get(id=domain_id)
                    instance.domains.add(domain)
                except AssessmentDomain.DoesNotExist:
                    pass

            # Handle deletion of specified existing attachments
            if attachment_ids_to_delete:
                CareplanAtachements.objects.filter(id__in=attachment_ids_to_delete).delete()

            # Process new temporary files as attachments
            if temporary_file_ids:
                temp_files = TemporaryFile.objects.filter(id__in=temporary_file_ids)
                attachments = []
                for temp_file in temp_files:
                    # Assuming you have a similar file moving function as in your Appointment example
                    old_key = temp_file.file.name
                    new_key = f"clients_pics/{old_key.split('/')[-1]}"

                    # Implement your file moving logic here
                    move_file_s3(old_key, new_key)

                    attachments.append(
                        CareplanAtachements(
                            careplan=instance,
                            attachement=f"{settings.MEDIA_URL}{new_key}",
                            name=temp_file.file.name.split("/")[-1],
                        )
                    )
                    temp_file.delete()

                # Bulk create new attachments
                CareplanAtachements.objects.bulk_create(attachments)

            return instance
