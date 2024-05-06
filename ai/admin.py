from django.contrib import admin

from ai.models import AIGeneratedReport


@admin.register(AIGeneratedReport)
class AIGeneratedReportsAdmin(admin.ModelAdmin):
    list_display = ("title", "user_type", "report_type", "start_date", "end_date", "created")
    list_filter = ("user_type", "report_type", "created")
