from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'profile_picture']

    # If needed, customize the form fields
    fieldsets = UserAdmin.fieldsets + (
        # Add the 'profile_picture' field in a new fieldset or add it to an existing one
        ('Additional info', {'fields': ('profile_picture',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        # Add 'profile_picture' to the fieldsets used when creating a new user, if necessary
        ('Additional info', {'fields': ('profile_picture',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)





# Register your models here.
