from django.contrib import admin

from system.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "is_read", "content", "created")
    list_filter = ("event", "is_read", "created")
