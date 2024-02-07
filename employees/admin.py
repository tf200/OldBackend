from django.contrib import admin
from .models import EmployeeProfile

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'department')
    search_fields = ('user__username', 'position', 'department')
    list_filter = ('position', 'department')
    