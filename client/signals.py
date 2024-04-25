from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from loguru import logger

from .models import ClientDetails, ClientStatusHistory


@receiver(pre_save, sender=ClientDetails)
def create_client_profile_status_history(
    sender: type[ClientDetails], instance: ClientDetails, **kwargs
):
    old_client = get_object_or_404(ClientDetails, id=instance.pk)

    if instance.status != old_client.status:
        # Status changed
        logger.debug("New ClientStatusHistory created!")
        ClientStatusHistory.objects.create(client=instance, status=instance.status)


@receiver(post_save, sender=ClientDetails)
def create_client_profile_status_history_on_create(
    sender: type[ClientDetails], instance: ClientDetails, created: bool, **kwargs
):
    if created:
        # Status changed
        ClientStatusHistory.objects.create(client=instance, status=instance.status)
