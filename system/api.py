from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import Router, UploadedFile
from ninja.pagination import paginate

from system.models import AttachmentFile, DBSettings, Notification
from system.schemas import (
    AttachmentFilePatch,
    AttachmentFileSchema,
    DBSettingsSchema,
    EmptyResponseSchema,
    ErrorResponseSchema,
    NotificationSchema,
)
from system.utils import NinjaCustomPagination

router = Router()


@router.get("/settings", response=DBSettingsSchema)
def settings(request: HttpRequest):
    return DBSettings.objects.all()


@router.get("/notifications", response=list[NotificationSchema])
@paginate(NinjaCustomPagination)
def notifications(request: HttpRequest):
    user = request.user
    return Notification.objects.filter(receiver=user).all()


@router.post(
    "/notifications/{id}/read",
    response={
        201: EmptyResponseSchema,
        404: ErrorResponseSchema,
        401: ErrorResponseSchema,
    },
)
def mark_as_read(request, id: int):
    try:
        notification = Notification.objects.get(id=id)

        if notification.receiver == request.user:
            notification.is_read = True
            notification.save()
            return 201, {}
        return 401, {"message", "Unauthorized action/request!"}
    except Notification.DoesNotExist:
        return 404, {"message": "Notification not found"}


@router.get("/attachments", response=list[AttachmentFileSchema])
@paginate(NinjaCustomPagination)
def attachments(request: HttpRequest):
    return AttachmentFile.objects.all()


@router.post("/attachments/upload", response=AttachmentFileSchema)
def upload_attachment(request: HttpRequest, file: UploadedFile):
    return AttachmentFile.objects.create(name=file.name, file=file, size=file.size)


@router.get("/attachments/{uuid}", response=AttachmentFileSchema)
def attachment_details(request: HttpRequest, uuid: UUID):
    return get_object_or_404(AttachmentFile, id=uuid)


@router.delete(
    "/attachments/{uuid}/delete", response={204: EmptyResponseSchema, 500: ErrorResponseSchema}
)
def delete_attachment(request: HttpRequest, uuid: UUID):
    try:
        AttachmentFile.objects.filter(id=uuid).delete()
        return 204, {}
    except Exception:
        logger.exception()  # type: ignore
    return 500, "Oops! something went wrong, please try again or later."


@router.patch("/attachments/{uuid}/update", response=AttachmentFileSchema)
def update_attachment(request: HttpRequest, uuid: UUID, attachment: AttachmentFilePatch):
    AttachmentFile.objects.filter(id=uuid).update(**attachment.dict(exclude_unset=True))
    return get_object_or_404(AttachmentFile, id=uuid)
