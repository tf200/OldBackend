from typing import Literal

from ninja import Field, ModelSchema, Schema

from client.models import ClientDetails, Contract, ContractType, Invoice
from employees.models import ClientMedication, ClientMedicationRecord
from system.models import AttachmentFile
from system.schemas import AttachmentFileSchema


class ContractSchema(ModelSchema):
    sender_id: int
    client_id: int
    attachments: list[AttachmentFileSchema]

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
    price_frequency: Literal["minute", "hourly", "daily", "weekly", "monthly"]
    care_type: Literal["​ambulante", "accommodation"]
    attachment_ids: list[str] = []

    class Meta:
        model = Contract
        exclude = ("id", "type", "sender", "client", "updated", "created")


class InvoiceSchema(ModelSchema):
    client_id: int

    class Meta:
        model = Invoice
        exclude = ("client",)


class ContractTypeSchema(ModelSchema):
    class Meta:
        model = ContractType
        fields = "__all__"


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
