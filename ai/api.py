from django.http import HttpRequest
from ninja import Router

from ai.schemas import ReportSchema
from ai.utils import ai_enhance_report

router = Router()


@router.post("/enhance-report", response=ReportSchema)
def enhance_reports(request: HttpRequest, report: ReportSchema):
    enhanced_report = ai_enhance_report(report.content)
    return ReportSchema(content=enhanced_report)


@router.post("/generate_summary/{int:client_id}/{str:start_date}/{str:end_date}")
def generate_report_summary(request: HttpRequest, start_date: str, end_date: str):

    return {}
