from django.contrib import admin

from system.models import AttachmentFile, DBSettings, Expense, Notification


@admin.register(DBSettings)
class DBSettingsAdmin(admin.ModelAdmin):
    list_display = ("option_name", "option_value", "option_type")
    list_filter = ("option_name", "option_type")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "is_read", "content", "created")
    list_filter = ("event", "is_read", "created")


@admin.register(AttachmentFile)
class AttachmentFileAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "size", "file", "is_used", "created")
    list_filter = ("is_used", "created", "updated")
    search_fields = ("id", "name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "desc", "created")
    list_filter = ("created",)
    search_fields = ("id",)
