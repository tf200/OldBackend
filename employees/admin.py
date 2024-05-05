from django.contrib import admin

from .models import (
    AiGeneratedWeeklyReports,
    Certification,
    ClientDetails,
    ClientGoals,
    ClientMedication,
    EmotionalState,
    EmployeeProfile,
    Feedback,
    GoalsReport,
    Observations,
    PhysicalState,
    ProgressReport,
    WeeklyReportSummary,
)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "department")
    search_fields = ("user__username", "position", "department")
    list_filter = ("position", "department")
    # filter_horizontal = ("groups",)


# Optional: Define a custom admin class to customize the admin interface
@admin.register(WeeklyReportSummary)
class WeeklyReportSummaryAdmin(admin.ModelAdmin):
    list_display = ("client", "created_at")  # Customize the list display fields
    list_filter = ("created_at", "client")  # Enable filtering by these fields
    search_fields = ("summary_text",)  # Enable search by summary text


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    pass


@admin.register(AiGeneratedWeeklyReports)
class AiGeneratedWeeklyReportsAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientDetails)
class ClientDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientGoals)
class ClientGoalsAdmin(admin.ModelAdmin):
    pass


@admin.register(EmotionalState)
class EmotionalStateAdmin(admin.ModelAdmin):
    pass


@admin.register(GoalsReport)
class GoalsReportAdmin(admin.ModelAdmin):
    pass


@admin.register(PhysicalState)
class PhysicalStateAdmin(admin.ModelAdmin):
    pass


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientMedication)
class ClientMedicationAdmin(admin.ModelAdmin):
    pass


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass


@admin.register(Observations)
class ObservationsAdmin(admin.ModelAdmin):
    pass
