from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import GoalsReport, WeeklyReportSummary
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from django.core.mail import send_mail

llm = ChatOpenAI(openai_api_key="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")

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "these are daily reports of our clients, I need you to write a detailed summary of these reports"),
    ("user", "{input}")
])

@shared_task
def summarize_weekly_reports():
    one_week_ago = timezone.now() - timedelta(days=7)
    reports = GoalsReport.objects.filter(created_at_sys__gte=one_week_ago).select_related('goal__client').order_by('goal__client')

    current_client = None
    current_client_reports = []
    for report in reports:
        if current_client != report.goal.client:
            if current_client_reports:
                summarize_and_save(current_client, current_client_reports)
            
            current_client = report.goal.client
            current_client_reports = [report.report_text]
        else:
            current_client_reports.append(report.report_text)
    
    if current_client_reports:
        summarize_and_save(current_client, current_client_reports)

def summarize_and_save(client, reports):
    reports_str = "\n".join(reports)  # Combine reports into a single string
    
    # Invoke your summarization chain
    chain = prompt_template | llm 
    summary_response = chain.invoke({"input": f"{reports_str}"})
    
    # Extract summary from the response
    summary_text = summary_response['output'].strip()
    
    # Save the summary to the database
    WeeklyReportSummary.objects.create(client=client, summary_text=summary_text)



@shared_task
def send_login_credentials(email, username, password):
    subject = 'Your new account'
    message = f'Hello,\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\nPlease change your password upon first login.'
    send_mail(
                subject=subject,
                message=message, 
                from_email='',
                recipient_list=[email],
                fail_silently= False
                
            )