from typing import Any, Generic, Optional, TypeAlias, TypeVar, Union

from easyaudit.models import CRUDEvent
from ninja import Field, ModelSchema, Schema

from adminmodif.models import Group
from system.models import AttachmentFile, DBSettings, Expense, Notification


class DBSettingsSchema(Schema):
    settings: dict[str, Any] = {}

    @staticmethod
    def resolve_settings(list) -> dict[str, Any]:
        return DBSettings.get_settings(refresh=True)


class NotificationSchema(ModelSchema):
    class Meta:
        model = Notification
        exclude = ["receiver"]


T = TypeVar("T")


class ResponseSchema(Schema, Generic[T]):
    data: list[T] = []


class ErrorResponseSchema(Schema):
    message: str


class EmptyResponseSchema(Schema):
    pass


class AttachmentFileSchema(ModelSchema):
    tag: str | None = None

    class Meta:
        model = AttachmentFile
        fields = "__all__"


class AttachmentFilePatch(Schema):
    name: str | None = None
    size: int | None = None
    is_used: bool | None = None
    tag: str | None


class ExpenseSchema(ModelSchema):
    attachments: Optional[list[AttachmentFileSchema]]

    class Meta:
        model = Expense
        fields = "__all__"

    @staticmethod
    def resolve_attachments(expense: Expense):
        return AttachmentFile.objects.filter(id__in=expense.attachment_ids).all()


class ExpenseSchemaInput(ModelSchema):
    class Meta:
        model = Expense
        exclude = ("id", "updated")


class ExpenseSchemaPatch(Schema):
    amount: int | None = None
    tax: float | None = None
    desc: str | None = None
    attachment_ids: list[str] | None = None


class ActivityLogSchema(ModelSchema):
    class Meta:
        model = CRUDEvent
        fields = "__all__"


class GroupSchema(ModelSchema):
    permissions: list[str]

    class Meta:
        model = Group
        exclude = ("permissions",)

    @staticmethod
    def resolve_permissions(group: Group) -> list[str]:
        return [perm.name for perm in group.permissions.all()]


class GroupSchemaInput(Schema):
    name: str
    permissions: list[str]


class GroupSchemaPatch(Schema):
    name: str | None = None
    permissions: list[str] | None = None


class GroupsListSchema(Schema):
    groups: list[int]
