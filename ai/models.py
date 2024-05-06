from django.db import models

from authentication.models import CustomUser


class AIGeneratedReport(models.Model):
    class ReportTypes(models.TextChoices):
        CLIENT_REPORTS_SUMMARY = ("client_reports_summary", "Client reports Summary")
        CLIENT_PROFILE_SUMMARY = ("client_profile_summary", "Client Profile Summary")
        CLIENT_GOALS_AND_OBJECTIVES_SUMMARY = (
            "client_goals_and_objectives_summary",
            "Client goals and objective summary",
        )
        EMPLOYEE_PERFORMANCE = ("employee_performance", "Employee Performance")

    class UserType(models.TextChoices):
        CLIENT = ("client", "Client")
        EMPLOYEE = ("employee", "Employee")

    report_type = models.CharField(choices=ReportTypes.choices)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)

    user = models.ForeignKey(
        CustomUser,
        related_name="generated_reports",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user_type = models.CharField(choices=UserType.choices)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    updated = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
