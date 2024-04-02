from django.contrib import admin

from .models import (
    CarePlan,
    CareplanAtachements,
    ClientTypeContactRelation,
    Contact,
    Invoice,
    InvoiceContract,
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


@admin.register(InvoiceContract)
class CareplanAtachementsAdmin(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(CarePlan)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(TemporaryFile)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientTypeContactRelation)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class InvoiceAdmin(admin.ModelAdmin):
    pass
