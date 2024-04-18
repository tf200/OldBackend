from uuid import UUID

from django.http import HttpRequest
from loguru import logger
from ninja import Router, UploadedFile
from ninja.pagination import paginate

from system.models import AttachmentFile, Notification
from system.schemas import (
    AttachmentFileSchema,
    EmptyResponseSchema,
    ErrorResponseSchema,
    NotificationSchema,
)
from system.utils import NinjaCustomPagination

router = Router()


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
