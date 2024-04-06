from typing import Any, Generic, TypeAlias, TypeVar, Union

from ninja import ModelSchema, Schema

from system.models import Notification


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
