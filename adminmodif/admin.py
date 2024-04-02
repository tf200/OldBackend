from django.contrib import admin
from django.utils import timezone

# Register your models here.
from .models import (  # Adjust the import path according to your app structure and model location
    Group,
    GroupMembership,
)

# Register your models here.
admin.site.register(Group)


class IsActiveFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the right admin sidebar
    title = "Is active"

    # Parameter for the filter that will be used in the URL query
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        # This returns a list of tuples. The first element in each tuple is the coded value
        # for the option that will appear in the URL query. The second element is the
        # human-readable name for the option that will appear in the right sidebar.
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        # This is where you process the selected filter option.
        if self.value() == "Yes":
            return (
                queryset.filter(
                    start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()
                )
                | queryset.filter(start_date__isnull=True, end_date__gte=timezone.now().date())
                | queryset.filter(start_date__lte=timezone.now().date(), end_date__isnull=True)
                | queryset.filter(start_date__isnull=True, end_date__isnull=True)
            )
        if self.value() == "No":
            return (
                queryset.exclude(
                    start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()
                )
                .exclude(start_date__isnull=True, end_date__gte=timezone.now().date())
                .exclude(start_date__lte=timezone.now().date(), end_date__isnull=True)
                .exclude(start_date__isnull=True, end_date__isnull=True)
            )


class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "start_date", "end_date", "is_active")
    list_filter = ("user", "group", IsActiveFilter)  # Use the custom filter here
    search_fields = (
        "user__username",
        "group__name",
    )  # Adjust based on your User and Group model fields


admin.site.register(GroupMembership, GroupMembershipAdmin)
