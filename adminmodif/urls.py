from django.urls import path
from .views import ListGroups , assign_group ,  list_employee_groups

urlpatterns = [
    path('groups/', ListGroups.as_view(), name='list_groups'),
    path('assign-group/', assign_group, name='assign_group_api'),
    path('user-groups/<int:employee_id>/', list_employee_groups, name='list-employee-groups'),

]