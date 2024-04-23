from typing import Literal

from ninja import Field, ModelSchema, Schema

from client.models import ClientDetails, Contract, ContractType, Invoice
from employees.models import ClientMedication, ClientMedicationRecord
from system.models import AttachmentFile
from system.schemas import AttachmentFileSchema


class ContractSchema(ModelSchema):
    sender_id: int
    client_id: int
    client_first_name: str | None
    client_last_name: str | None
    client_email: str | None
    attachments: list[AttachmentFileSchema]
    price: float
    price_frequency: Literal["minute", "hourly", "daily", "weekly", "monthly"]
    care_type: Literal["ambulante", "accommodation"]
    status: Literal["approved", "draft", "terminated"] = "draft"

    @staticmethod
    def resolve_client_first_name(contract: Contract) -> str | None:
        return contract.client.first_name

    @staticmethod
    def resolve_client_last_name(contract: Contract) -> str | None:
        return contract.client.last_name

    @staticmethod
    def resolve_client_email(contract: Contract) -> str | None:
        return contract.client.email

    @staticmethod
    def resolve_attachments(contract: Contract) -> list[AttachmentFileSchema]:
        return [
            AttachmentFileSchema.from_orm(AttachmentFile.objects.get(id=uuid))
            for uuid in contract.attachment_ids
        ]

    class Meta:
        model = Contract
        exclude = ("sender", "client", "attachment_ids")


class ContractSchemaInput(ModelSchema):
    sender_id: int
    client_id: int
    type_id: int
    price: float
    price_frequency: Literal["minute", "hourly", "daily", "weekly", "monthly"]
    care_type: Literal["ambulante", "accommodation"]
    attachment_ids: list[str] = []
    status: Literal["approved", "draft", "terminated"] = "draft"

    class Meta:
        model = Contract
        exclude = ("id", "type", "sender", "client", "updated", "created")


# class ContractSchemaPatch(ModelSchema):
#     sender_id: int | None
#     client_id: int | None
#     type_id: int | None
#     price_frequency: Literal["minute", "hourly", "daily", "weekly", "monthly"] | None
#     care_type: Literal["​ambulante", "accommodation"] | None
#     attachment_ids: list[str] | None

#     class Meta:
#         model = Contract
#         exclude = ("id", "type", "sender", "client", "updated", "created")


class InvoiceSchema(ModelSchema):
    client_id: int

    class Meta:
        model = Invoice
        exclude = ("client",)


class ContractTypeSchema(ModelSchema):
    class Meta:
        model = ContractType
        fields = "__all__"


class ContractTypeInput(Schema):
    name: str


class ClientDetailsSchema(ModelSchema):
    class Meta:
        model = ClientDetails
        fields = "__all__"


class ClientMedicationSchema(ModelSchema):
    client_id: int | None
    administered_by_id: int | None

    class Meta:
        model = ClientMedication
        # fields = "__all__"
        exclude = ("client", "administered_by", "updated")


class MedicationRecordSchema(ModelSchema):
    client_medication_id: int | None = None

    class Meta:
        model = ClientMedicationRecord
        exclude = ("client_medication",)


class MedicationRecordInput(Schema):
    status: Literal["taken", "not_taken", "awaiting"]
    reason: str | None
