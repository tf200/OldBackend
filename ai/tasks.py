from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ai.models import AIGeneratedReport
from celery import shared_task
from client.models import ClientDetails
from employees.models import GoalsReport, ProgressReport, WeeklyReportSummary

SYSTEM_PROMPT: str = """
These are daily reports of our clients, I need you to write a detailed summary of these reports,
And you MUST answer in Dutch and NOTHING ELSE.
"""


llm = ChatOpenAI(openai_api_key=settings.OPENAI_KEY)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "{input}"),
        ("user", "Summary:"),
    ]
)


@shared_task
def summarize_client_reports():
    weeks_ago = timezone.now() - timedelta(weeks=8)
    now = timezone.now()

    for client in ClientDetails.objects.filter(status="In Care").all():
        client_reports = ProgressReport.objects.filter(client=client, created__gte=weeks_ago).all()

        client_info = (
            f"#Client info: id={client.pk}, full name: {client.first_name} {client.last_name}\n\n"
        )

        concatenated_reports: str = "# Client Reports:\n"
        for report in client_reports:
            concatenated_reports += f"#Report ({report.pk}):\n#title: {report.title}\n#date: {report.date.date()}\n<content>{report.report_text}</content>\n\n---\n"

        print(client_info + concatenated_reports)

        summary: str = ai_summarize.delay(client_info + concatenated_reports)
        # Create a summary report
        AIGeneratedReport.objects.create(
            title=f"Generated client report ({client.pk}) from ({weeks_ago.date()} - {now.date()})",
            content=summary,
            user=client.user,
            user_type=AIGeneratedReport.UserType.CLIENT,
            report_type=AIGeneratedReport.ReportTypes.CLIENT_REPORTS_SUMMARY,
            start_date=weeks_ago,
            end_date=now,
        )


@shared_task
def ai_summarize(content: str) -> str:
    # Combine reports into a single string

    # Invoke your summarization chain
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"input": f"{content}"})


@shared_task
def summarize_weekly_reports():
    weeks_ago = timezone.now() - timedelta(weeks=8)
    reports = (
        GoalsReport.objects.filter(created_at_sys__gte=weeks_ago)
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
