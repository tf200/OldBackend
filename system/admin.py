from django.contrib import admin

from system.models import AttachmentFile, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "is_read", "content", "created")
    list_filter = ("event", "is_read", "created")


@admin.register(AttachmentFile)
class AttachmentFileAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "size", "file", "is_used", "created")
    list_filter = ("is_used", "created", "updated")
    search_fields = ("id", "name")
