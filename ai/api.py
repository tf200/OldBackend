from django.http import HttpRequest
from ninja import Router

from ai.schemas import ReportSchema
from ai.utils import ai_enhance_report

router = Router()


@router.post("/enhance-report", response=ReportSchema)
def enhance_reports(request: HttpRequest, report: ReportSchema):
    enhanced_report = ai_enhance_report(report.content)
    return ReportSchema(content=enhanced_report)
