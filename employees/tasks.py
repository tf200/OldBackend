from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .models import GoalsReport, WeeklyReportSummary

SYSTEM_PROMPT: str = """
These are daily reports of our clients, I need you to write a detailed summary of these reports,
And you MUST answer in Dutch and NOTHING ELSE.
"""

llm = ChatOpenAI(openai_api_key=settings.OPENAI_KEY)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "{input}"),
    ]
)


# @shared_task
def summarize_weekly_reports():
    one_week_ago = timezone.now() - timedelta(days=7)
    reports = (
        GoalsReport.objects.filter(created_at_sys__gte=one_week_ago)
        .select_related("goal__client")
        .order_by("goal__client")
    )

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
    summary_text = summary_response.content

    # Save the summary to the database
    WeeklyReportSummary.objects.create(client=client, summary_text=summary_text)


@shared_task
def send_login_credentials(email, username, password):
    subject = "Your new account"
    message = f"Hello,\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\n\nPlease change your password upon first login."

    send_mail(
        subject=subject,
        message=message,
        recipient_list=[email],
        fail_silently=False,
    )
