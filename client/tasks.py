from .models import ClientEmergencyContact 
from employees.models import ProgressReport
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings




@shared_task
def send_progress_report_email(progress_report_id , report_text):
    try:
        print(progress_report_id)
        progress_report = ProgressReport.objects.get(id=progress_report_id)
        print(progress_report.client)
        emergency_contacts = ClientEmergencyContact.objects.filter(client=progress_report.client, auto_reports=True)
        print(emergency_contacts)
        for contact in emergency_contacts:
            send_mail(
                subject='Progress Report Update',
                message=f'{report_text}',  # Customize your message
                from_email='farjiataha@gmail.com',
                recipient_list=[contact.email],
                fail_silently= False
                
            )
            
        print('task finnished')
    except ProgressReport.DoesNotExist:
        pass 
