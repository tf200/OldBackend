import datetime

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import paginate

from ai.filters import AIGeneratedReportSchemaFilter
from ai.models import AIGeneratedReport
from ai.schemas import AIGeneratedReportSchema, ReportSchema
from ai.tasks import ai_summarize
from ai.utils import ai_enhance_report
from client.models import ClientDetails
from client.schemas import DatePeriodSchema, ObjectiveProgressReportSchema
from employees.models import DomainObjective, ProgressReport
from system.utils import NinjaCustomPagination

router = Router()


@router.post("/enhance-report", response=ReportSchema)
def enhance_reports(request: HttpRequest, report: ReportSchema):
    enhanced_report = ai_enhance_report(report.content)
    return ReportSchema(content=enhanced_report)


@router.get("/generated_summaries", response=list[AIGeneratedReportSchema])
@paginate(NinjaCustomPagination)
def get_all_generated_reports(request: HttpRequest, filters: AIGeneratedReportSchemaFilter = Query()):  # type: ignore
    return filters.filter(AIGeneratedReport.objects.all())


@router.get("/generated_summaries/{int:client_id}", response=list[AIGeneratedReportSchema])
@paginate(NinjaCustomPagination)
def get_all_generated_client_reports(request: HttpRequest, client_id: int, filters: AIGeneratedReportSchemaFilter = Query()):  # type: ignore
    client = get_object_or_404(ClientDetails, id=client_id)
    return filters.filter(AIGeneratedReport.objects.filter(user=client.user).all())


@router.post(
    "/generate_report_summary/{int:client_id}/{str:start_date}/{str:end_date}",
    response=AIGeneratedReportSchema,
)
def generate_report_summary(request: HttpRequest, client_id: int, start_date: str, end_date: str):
    client = get_object_or_404(ClientDetails, id=client_id)
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    client_reports = ProgressReport.objects.filter(
        client=client, created__gte=start, created__lte=end
    ).all()

    client_info = (
        f"#Client info: id={client.pk}, full name: {client.first_name} {client.last_name}\n\n"
    )

    concatenated_reports: str = "# Client Reports:\n"
    for report in client_reports:
        concatenated_reports += f"#Report ({report.pk}):\n#title: {report.title}\n#date: {report.date.date()}\n<content>{report.report_text}</content>\n\n---\n"

    summary: str = ai_summarize(client_info + concatenated_reports)
    # Create a summary report
    return AIGeneratedReport.objects.create(
        title=f"Generated client report ({client.pk}) from ({start} - {end})",
        content=summary,
        user=client.user,
        user_type=AIGeneratedReport.UserType.CLIENT,
        report_type=AIGeneratedReport.ReportTypes.CLIENT_REPORTS_SUMMARY,
        start_date=start,
        end_date=end,
    )


@router.post(
    "/objectives/{int:objective_id}/progress-reports/generate",
    response=ObjectiveProgressReportSchema | None,
)
def generate_objective_progress_report(
    request: HttpRequest,
    objective_id: int,
    payload: DatePeriodSchema,
):
    # Generate the objective reports for the period
    objective = get_object_or_404(DomainObjective, id=objective_id)

    return objective.ai_generate_progress_report(
        start_date=str(payload.start_date), end_date=str(payload.end_date)
    )
