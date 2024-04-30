from typing import Any, Generic, TypeAlias, TypeVar, Union

from ninja import ModelSchema, Schema

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
    class Meta:
        model = Expense
        fields = "__all__"


class ExpenseSchemaInput(ModelSchema):
    class Meta:
        model = Expense
        exclude = ("id", "updated")


class ExpenseSchemaPatch(Schema):
    amount: int | None = None
    desc: str | None = None
