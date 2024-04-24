from django.contrib import admin

from employees.models import ClientMedicationRecord

from .models import (
    CarePlan,
    CareplanAtachements,
    ClientStatusHistory,
    Contact,
    Contract,
    ContractType,
    ContractWorkingHours,
    Invoice,
    InvoiceContract,
    Sender,
    SenderContactRelation,
    TemporaryFile,
)

# class ClientDetailsAdmin(admin.ModelAdmin):
#     # This is optional, to customize how the model appears in the admin
#     list_display = ('user', 'organisation', 'location', 'departement', 'gender', 'filenumber')
#     search_fields = ('user__username', 'organisation', 'location')
#     list_filter = ('organisation', 'location', 'departement', 'gender')

#     # If you need to customize the form
#     # fieldsets = (
#     #     (None, {
#     #         'fields': ('user', 'organisation', 'location', 'departement', 'gender', 'filenumber')
#     #     }),
#     # )

# # Register your models here
# admin.site.register(ClientDetails, ClientDetailsAdmin)


@admin.register(CareplanAtachements)
class CareplanAttachmentsAdmin(admin.ModelAdmin):
    list_display = ("id", "careplan", "name", "created_at")  # Customize columns displayed
    list_filter = ("created_at",)  # Enable filtering by these fields
    search_fields = ("name", "careplan__description")  # Enable search by these fields


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "start_date",
        "end_date",
        "reminder_period",
        "price",
        "price_frequency",
        "created",
    )

    list_filter = ("price_frequency", "type", "created")


@admin.register(InvoiceContract)
class CareplanAtachementsAdmin(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "due_date",
        "total_amount",
        "status",
        "issue_date",
    )
    list_filter = ("due_date", "status", "issue_date")
    search_fields = ("invoice_number",)


@admin.register(CarePlan)
class CarePlanAdmin(admin.ModelAdmin):
    pass


@admin.register(TemporaryFile)
class TemporaryFileAdmin(admin.ModelAdmin):
    pass


@admin.register(SenderContactRelation)
class SenderContactRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = ("name", "email_adress", "phone_number", "client_number")


@admin.register(ClientMedicationRecord)
class ClientMedicationRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientStatusHistory)
class ClientStatusHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ContractWorkingHours)
class ContractWorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("contract", "minutes", "datetime")
    list_filter = ("datetime",)
    search_fields = (
        "id",
        "contract__id",
        "datetime",
    )
