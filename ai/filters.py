from typing import Literal, Optional

from ninja import FilterSchema


class AIGeneratedReportSchemaFilter(FilterSchema):
    report_type: Optional[
        Literal[
            "client_reports_summary",
            "client_profile_summary",
            "client_goals_and_objectives_summary",
            "employee_performance",
        ]
    ] = None
    user_type: Optional[Literal["client", "employee"]] = None
