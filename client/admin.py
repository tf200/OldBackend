
from django.contrib import admin
from .models import ClientDetails

class ClientDetailsAdmin(admin.ModelAdmin):
    # This is optional, to customize how the model appears in the admin
    list_display = ('user', 'organisation', 'location', 'departement', 'gender', 'filenumber')
    search_fields = ('user__username', 'organisation', 'location')
    list_filter = ('organisation', 'location', 'departement', 'gender')

    # If you need to customize the form
    # fieldsets = (
    #     (None, {
    #         'fields': ('user', 'organisation', 'location', 'departement', 'gender', 'filenumber')
    #     }),
    # )

# Register your models here
admin.site.register(ClientDetails, ClientDetailsAdmin)