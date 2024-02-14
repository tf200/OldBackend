from django.urls import path
from .views import ListGroups , assign_group , UserGroupsAPIView

urlpatterns = [
    path('groups/', ListGroups.as_view(), name='list_groups'),
    path('assign-group/', assign_group, name='assign_group_api'),
    path('user-groups/<int:user_id>/', UserGroupsAPIView.as_view(), name='user_groups'),

]