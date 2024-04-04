from django.contrib import admin

from .models import Appointment, AppointmentAttachment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("title", "appointment_type", "start_time", "end_time")


@admin.register(AppointmentAttachment)
class AppointmentAttachment(admin.ModelAdmin):
    pass
