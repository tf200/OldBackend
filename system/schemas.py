from typing import Any, Generic, TypeAlias, TypeVar, Union

from ninja import ModelSchema, Schema

from system.models import AttachmentFile, DBSettings, Notification


class DBSettingsSchema(Schema):
    settings: dict[str, Any] = {}

    @staticmethod
    def resolve_settings(list) -> dict[str, Any]:
        return DBSettings.get_settings()


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
