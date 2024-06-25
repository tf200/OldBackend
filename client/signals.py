from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from loguru import logger

from employees.models import ProgressReport
from system.models import AttachmentFile

from .models import ClientDetails, ClientEmergencyContact, ClientStatusHistory, Incident


@receiver(pre_save, sender=ClientDetails)
def create_client_profile_status_history(
    sender: type[ClientDetails], instance: ClientDetails, **kwargs
):
    try:
        old_client = ClientDetails.objects.get(id=instance.pk)

        # Register the client status as record or history
        if instance.status != old_client.status:
            # Status changed
            logger.debug("New ClientStatusHistory created!")
            ClientStatusHistory.objects.create(client=instance, status=instance.status)

        # Delete unused attachment files during client update.
        if instance.identity_attachment_ids != old_client.identity_attachment_ids:
            logger.debug("deleting unsued client attachment!")
            attachments_ids = set(
                set(old_client.identity_attachment_ids) - set(instance.identity_attachment_ids)
            )  # Attachment ids to be deleted
            AttachmentFile.objects.filter(id__in=attachments_ids).delete()

    except ClientDetails.DoesNotExist:
        logger.debug(f"Client not found")


@receiver(post_save, sender=ClientDetails)
def create_client_profile_status_history_on_create(
    sender: type[ClientDetails], instance: ClientDetails, created: bool, **kwargs
):
    if created:
        # Status changed
        ClientStatusHistory.objects.create(client=instance, status=instance.status)


# send progree report to client emergency contacts once created
@receiver(post_save, sender=ProgressReport)
def send_progress_report_to_client_emergency_contacts(
    sender: type[ProgressReport], instance: ProgressReport, created: bool, **kwargs
):
    # if created:
    #     # Send progress report to client emergency contacts
    #     instance.send_progress_report_to_emergency_contacts()
    pass


# Send incident report to client emergency contacts once created
@receiver(post_save, sender=Incident)
def send_incident_to_client_emergency_contacts(
    sender: type[Incident], instance: Incident, created: bool, **kwargs
):
    if created:
        # Send incident report to client emergency contacts
        instance.send_incident_to_emergency_contacts()


# Send verification email to client emergency contacts once created
@receiver(post_save, sender=ClientEmergencyContact)
def send_verification_email_for_emergency_contacts(
    sender: type[ClientEmergencyContact], instance: ClientEmergencyContact, created: bool, **kwargs
):
    if created:
        # Send ClientEmergencyContact report to client emergency contacts
        instance.send_verification_email()
