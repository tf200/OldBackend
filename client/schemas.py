from datetime import date, datetime
from typing import Any, Literal, Optional

from loguru import logger
from ninja import Field, FilterSchema, ModelSchema, Schema

from client.models import (
    ClientCurrentLevel,
    ClientDetails,
    ClientState,
    ClientStatusHistory,
    Contract,
    ContractType,
    ContractWorkingHours,
    DomainGoal,
    DomainObjective,
    GoalHistory,
    Invoice,
    InvoiceHistory,
    ObjectiveHistory,
)
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
    sender_name: str

    @staticmethod
    def resolve_sender_name(contract: Contract) -> str:
        if contract.sender and contract.sender.name:
            return contract.sender.name
        return ""

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
        files: list[AttachmentFileSchema] = []

        for uuid in contract.attachment_ids:
            try:
                files.append(AttachmentFileSchema.from_orm(AttachmentFile.objects.get(id=uuid)))
            except AttachmentFile.DoesNotExist:
                logger.error(f"AttachmentFile not found: {uuid}")

        return files

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


class InvoiceHistorySchema(ModelSchema):
    class Meta:
        model = InvoiceHistory
        fields = "__all__"


class InvoiceSchema(ModelSchema):
    client_id: int
    history: list[InvoiceHistorySchema] = []
    total_paid_amount: float = 0
    sender_id: int | None
    sender_name: str

    class Meta:
        model = Invoice
        exclude = ("client",)

    @staticmethod
    def resolve_total_paid_amount(invoice: Invoice) -> float:
        return invoice.total_paid_amount()

    @staticmethod
    def resolve_sender_name(invoice: Invoice) -> str:
        if invoice.client.sender and invoice.client.sender.name:
            return invoice.client.sender.name
        return ""

    @staticmethod
    def resolve_sender_id(invoice: Invoice) -> int:
        if invoice.client.sender:
            return invoice.client.sender.pk
        return 0


class InvoiceHistoryInput(ModelSchema):
    invoice_status: Optional[
        Literal[
            "outstanding", "partially_paid", "paid", "expired", "overpaid", "imported", "concept"
        ]
    ] = None

    class Meta:
        model = InvoiceHistory
        exclude = ("id", "invoice", "created", "updated")


class InvoiceSchemaPatch(Schema):
    due_date: datetime | None = None
    payment_method: Literal["bank_transfer", "credit_card", "check", "cash"] | None = None
    status: (
        Literal[
            "outstanding", "partially_paid", "paid", "expired", "overpaid", "imported", "concept"
        ]
        | None
    ) = None
    invoice_details: list[dict[str, Any]] | None = None


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
    administered_by_name: str | None
    unset_medications: int | None

    class Meta:
        model = ClientMedication
        # fields = "__all__"
        exclude = ("client", "administered_by", "updated")

    @staticmethod
    def resolve_unset_medications(medication: ClientMedication) -> int:
        return int(
            medication.records.filter(  # type: ignore
                status=ClientMedicationRecord.Status.AWAITING
            ).count()
        )

    @staticmethod
    def resolve_administered_by_name(medication: ClientMedication) -> str:
        return f"{medication.administered_by.last_name} {medication.administered_by.last_name}"


class MedicationRecordSchema(ModelSchema):
    client_medication_id: int | None = None

    class Meta:
        model = ClientMedicationRecord
        exclude = ("client_medication",)


class MedicationRecordFilterSchema(FilterSchema):
    created: date | None = Field(None, q="created__date")
    status: Literal["awaiting", "taken", "not_taken"] | None = None


class MedicationRecordInput(Schema):
    status: Literal["taken", "not_taken", "awaiting"]
    reason: str | None


class ClientStatusHistorySchema(ModelSchema):
    client_id: int

    class Meta:
        model = ClientStatusHistory
        exclude = ("client",)


class ContractWorkingHoursSchema(ModelSchema):
    contract_id: int

    class Meta:
        model = ContractWorkingHours
        exclude = ("contract",)


class ContractWorkingHoursInput(ModelSchema):
    class Meta:
        model = ContractWorkingHours
        exclude = ("contract", "id")


class ContractWorkingHoursPatch(Schema):
    minutes: int | None = None
    datetime: Optional[datetime] = None  # type: ignore
    notes: str | None = None


class DomainObjectiveSchema(ModelSchema):
    goal_id: int
    client_id: int

    class Meta:
        model = DomainObjective
        exclude = ("goal", "client")


class DomainObjectiveInput(ModelSchema):

    class Meta:
        model = DomainObjective
        exclude = ("created", "updated", "goal", "client", "id")


class DomainObjectivePatch(Schema):
    title: str | None = None
    desc: str | None = None
    rating: float | None = None


class DomainGoalSchema(ModelSchema):
    domain_id: int
    client_id: int
    objectives: list[DomainObjectiveSchema]
    main_goal_rating: float

    class Meta:
        model = DomainGoal
        exclude = ("domain", "client")

    @staticmethod
    def resolve_main_goal_rating(domain_goal: DomainGoal) -> float:
        return domain_goal.main_goal_rating()


class DomainGoalInput(ModelSchema):
    domain_id: int

    class Meta:
        model = DomainGoal
        exclude = ("domain", "created", "updated", "id", "client")


class DomainGoalPatch(Schema):
    title: str | None = None
    desc: str | None = None


class GoalHistorySchema(ModelSchema):
    class Meta:
        model = GoalHistory
        exclude = ("id", "goal")


class ObjectiveHistorySchema(ModelSchema):
    class Meta:
        model = ObjectiveHistory
        exclude = ("id", "objective")


class ClientCurrentLevelSchema(ModelSchema):
    domain_id: int

    class Meta:
        model = ClientCurrentLevel
        exclude = ("client", "domain")


class ClientCurrentLevelInput(Schema):
    level: float
    domain_id: int


class ClientCurrentLevelPatch(Schema):
    level: float | None = None
    domain_id: int | None = None


class ClientStateSchema(ModelSchema):
    client_id: int

    class Meta:
        model = ClientState
        exclude = ("client",)


class ClientStateSchemaInput(ModelSchema):
    client_id: int
    type: Literal["emotional", "physical"]
    created: Optional[datetime] = None

    class Meta:
        model = ClientState
        exclude = ("client", "updated", "id")


class ClientStateSchemaPatch(Schema):
    value: Optional[int] = None
    content: Optional[str] = None
    created: Optional[datetime] = None
