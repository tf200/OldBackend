from typing import Any, Optional

from django.conf import settings
from django.core.mail import send_mail
from loguru import logger
from ninja import Field, Schema
from ninja.pagination import PaginationBase

from celery import shared_task


@shared_task
def send_mail_async(*args, recipient_list=None, **kwargs):
    if recipient_list is not None:
        logger.debug("Send an email to:", recipient_list)
        return send_mail(*args, recipient_list=recipient_list, **kwargs)


class NinjaCustomPagination(PaginationBase):
    class Input(Schema):
        page: int | None = Field(None, gt=0)

    class Output(Schema):
        results: list[Any]
        page_size: int
        count: int

    items_attribute: str = "results"

    def __init__(self, page_size: int = settings.NINJA_PAGINATION_PER_PAGE, **kwargs: Any) -> None:
        self.page_size = page_size
        super().__init__(**kwargs)

    def paginate_queryset(self, queryset, pagination: Input, **params):
        if pagination.page is None:
            pagination.page = 1

        offset = (pagination.page - 1) * self.page_size

        return {
            "results": queryset[offset : offset + self.page_size],
            "count": self._items_count(queryset),
            "page_size": self.page_size,
        }
