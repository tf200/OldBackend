from django.contrib import admin

# Register your models here.
from .models import Group  # Adjust the import path according to your app structure and model location

# Register your models here.
admin.site.register(Group)