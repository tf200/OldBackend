from django.contrib import admin

from .models import EmployeeProfile

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'position', 'department')
    search_fields = ('first_name', 'last_name', 'position', 'department')