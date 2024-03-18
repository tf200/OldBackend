from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Location
from django.utils.html import format_html


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'profile_picture', 'show_password']

    # If needed, customize the form fields
    fieldsets = UserAdmin.fieldsets + (
        # Add the 'profile_picture' field in a new fieldset
        ('Additional info', {'fields': ('profile_picture',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        # Add 'profile_picture' to the fieldsets used when creating a new user
        ('Additional info', {'fields': ('profile_picture',)}),
    )

    def show_password(self, obj):
        """
        Display the password hash. This method is NOT recommended for production environments.
        """
        return format_html('<span style="word-break: break-all;">{}</span>', obj.password)
    show_password.short_description = "Password Hash"

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Location)


# Register your models here.
