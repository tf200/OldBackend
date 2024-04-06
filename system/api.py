from django.http import HttpRequest
from django.shortcuts import render
from ninja import Router
from ninja.pagination import paginate

from system.models import Notification
from system.schemas import EmptyResponseSchema, ErrorResponseSchema, NotificationSchema
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
