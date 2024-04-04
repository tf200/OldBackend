from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from authentication.models import CustomUser
from client.models import ClientDetails
from employees.models import EmployeeProfile, Notification

from .models import Appointment


@receiver(post_save, sender=Appointment)
def appointment_created(sender, instance: Appointment, created, **kwargs):
    employees: list[EmployeeProfile] = list(instance.employees.all())
    clients: list[ClientDetails] = list(instance.clients.all())
    receiver_list: list[CustomUser] = [p.user for p in (employees + clients)]

    if created:
        print("signal: appointment created")
        # Sending notification for all employees and clients
        for user in receiver_list:
            # send a notification: appointment created
            notification = Notification.objects.create(
                title="Appointment created",
                event=Notification.EVENTS.APPOINTMENT_CREATED,
                content=f"A new appointment has been scheduled at {instance.start_time}.",
                receiver=user,
            )

            message = f"A new appointment has been scheduled:\n\ntitle: {instance.title}\nstart: {instance.start_time}."
            notification.notify(email_title="Appointment created", email_content=message)
    else:
        # Appointment updated
        pass


@receiver(pre_save, sender=Appointment)
def appointment_rescheduled_or_canceled(sender, instance: Appointment, **kwargs):
    if instance.pk is not None:
        old_instance: Appointment = Appointment.objects.filter(id=instance.id).get()

        employees: list[EmployeeProfile] = list(instance.employees.all())
        clients: list[ClientDetails] = list(instance.clients.all())
        receiver_list: list[CustomUser] = [p.user for p in (employees + clients)]

        if old_instance.start_time != instance.start_time:
            print("signal: appointment rescheduled")

            # The appointment has been rescheduled
            # Sending notification for all employees and clients
            for user in receiver_list:
                # send a notification: appointment created
                notification = Notification.objects.create(
                    title="Appointment rescheduled",
                    event=Notification.EVENTS.APPOINTMENT_RESCHEDULED,
                    content=f"The appointment #{instance.id} has been rescheduled to {instance.start_time}.",
                    receiver=user,
                )

                message = f"The appointment #{instance.id} has been rescheduled:\n\ntitle: {instance.title}\nstart: {instance.start_time}."
                notification.notify(email_title="Appointment rescheduled", email_content=message)

        if (
            old_instance.status != old_instance.STATUS.CANCELED
            and instance.status == old_instance.STATUS.CANCELED
        ):
            # Appointment updated (check for cancelation)
            print("signal: appointment canceled")

            for user in receiver_list:
                # send a notification: appointment canceled
                notification = Notification.objects.create(
                    title="Appointment canceled",
                    event=Notification.EVENTS.APPOINTMENT_CANCELED,
                    content=f"The appointment #{instance.id} has been canceled.",
                    receiver=user,
                )

                message = f"The appointment #{instance.id} has been canceled."
                notification.notify(email_title="Appointment canceled", email_content=message)


@receiver(post_delete, sender=Appointment)
def appointment_deleted(sender, instance: Appointment, **kwargs):

    if instance:
        employees: list[EmployeeProfile] = list(instance.employees.all())
        clients: list[ClientDetails] = list(instance.clients.all())
        receiver_list: list[CustomUser] = [p.user for p in (employees + clients)]

        print("signal: appointment canceled/deleted")

        for user in receiver_list:
            # send a notification: appointment canceled
            notification = Notification.objects.create(
                title="Appointment canceled",
                event=Notification.EVENTS.APPOINTMENT_CANCELED,
                content=f"The appointment #{instance.id} has been canceled.",
                receiver=user,
            )

            message = f"The appointment #{instance.id} has been canceled."
            notification.notify(email_title="Appointment canceled", email_content=message)
