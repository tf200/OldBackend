from .models import ClientEmergencyContact , ProgressReport
from celery import shared_task
from django.core.mail import send_mail





@shared_task
def send_progress_report_email(progress_report_id):
    try:
        progress_report = ProgressReport.objects.get(id=progress_report_id)
        emergency_contacts = ClientEmergencyContact.objects.filter(client=progress_report.client, auto_reports=True)
        
        for contact in emergency_contacts:
            send_mail(
                subject='Progress Report Update',
                message='Here is the progress report...', 
                from_email='your_email@example.com',
                recipient_list=[contact.email],
            )
    except ProgressReport.DoesNotExist:
        pass 
