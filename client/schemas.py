from typing import Literal

from ninja import Field, ModelSchema, Schema

from client.models import ClientDetails, ContractType
from employees.models import ClientMedication, ClientMedicationRecord


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
