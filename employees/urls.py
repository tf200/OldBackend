
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', CurrentUserProfileView.as_view(), name='current-user-profile'),
    path('progress_report/create/', ProgressReportCreateView.as_view(), name='progress_report_create'),
    path('progress_report/retrieve/<int:pk>/', ProgressReportRetrieveView.as_view(), name='progress_report_retrieve'),
    path('progress_report/list/<int:client>/', ProgressReportListView.as_view(), name='progress_report_list'),
    path('progress_report/update/<int:pk>/', ProgressReportUpdateView.as_view(), name='progress_report_update'),
    path('progress_report/delete/<int:pk>/', ProgressReportDeleteView.as_view(), name='progress_report_delete'),
]