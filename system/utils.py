from django.core.mail import send_mail

from celery import shared_task


@shared_task
def send_mail_async(*args, **kwargs):
    return send_mail(*args, **kwargs)
