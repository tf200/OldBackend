from django.contrib import admin

from .models import Assessment, AssessmentDomain


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("domain", "level", "content", "updated", "created")


@admin.register(AssessmentDomain)
class AssessmentDomainAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
