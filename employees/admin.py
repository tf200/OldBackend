from django.contrib import admin

from .models import EmployeeProfile, WeeklyReportSummary


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "department")
    search_fields = ("user__username", "position", "department")
    list_filter = ("position", "department")


# Optional: Define a custom admin class to customize the admin interface
class WeeklyReportSummaryAdmin(admin.ModelAdmin):
    list_display = ("client", "created_at")  # Customize the list display fields
    list_filter = ("created_at", "client")  # Enable filtering by these fields
    search_fields = ("summary_text",)  # Enable search by summary text


# Register the model and the admin class with the admin site
admin.site.register(WeeklyReportSummary, WeeklyReportSummaryAdmin)
