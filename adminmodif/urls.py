from django.urls import path
from .views import ListGroups , assign_group

urlpatterns = [
    path('groups/', ListGroups.as_view(), name='list_groups'),
    path('assign-group/', assign_group, name='assign_group_api'),

]