
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', CurrentUserProfileView.as_view(), name='current-user-profile'),

    path('progress_report/create/', ProgressReportCreateView.as_view(), name='progress_report_create'),
    path('progress_report/retrieve/<int:pk>/', ProgressReportRetrieveView.as_view(), name='progress_report_retrieve'),
    path('progress_report/list/<int:client>/', ProgressReportListView.as_view(), name='progress_report_list'),
    path('progress_report/update/<int:pk>/', ProgressReportUpdateView.as_view(), name='progress_report_update'),
    path('progress_report/delete/<int:pk>/', ProgressReportDeleteView.as_view(), name='progress_report_delete'),

    path('measurment_rud/<int:pk>/' , ClientMeasurmentRUDView.as_view() , name='measurment_rud' ),
    path('measurment_cl/' ,ClientMeasurmentCLView.as_view() , name = 'measurment_cl'),
    path('measurment_list/<int:client>/' ,ClientMeasurmentListView.as_view() , name = 'measurment_list'),

    path('observations_rud/<int:pk>/' , ClientObservationsRUDView.as_view() , name='observations_rud' ),
    path('observations_cl/' ,ClientObservationsCreateView.as_view() , name = 'observations_cl'),
    path('observations_list/<int:client>/' ,ClientObservationsListView.as_view() , name = 'observations_list'),

    path('feedback_rud/<int:pk>/' , ClientFeedbackRUDView.as_view() , name='feedback_rud' ),
    path('feedback_cl/' ,ClientFeedbackCreateView.as_view() , name = 'feedback_cl'),
    path('feedback_list/<int:client>/' ,ClientFeedbackListView.as_view() , name = 'feedback_list'),

    path('emotionalstate_rud/<int:pk>/' , ClientEmotionalStateRUDView.as_view() , name='emotionalstate_rud' ),
    path('emotionalstate_cl/' ,ClientEmotionalStateCreateView.as_view() , name = 'emotionalstate_cl'),
    path('emotionalstate_list/<int:client>/' ,ClientEmotionalStateListView.as_view() , name = 'emotionalstate_list'),

    path('physicalstate_rud/<int:pk>/' , ClientPhysicalStateRUDView.as_view() , name='physicalstate_rud' ),
    path('physicalstate_cl/' ,ClientPhysicalStateCreateView.as_view() , name = 'physicalstate_cl'),
    path('physicalstate_list/<int:client>/' ,ClientPhysicalStateListView.as_view() , name = 'physicalstate_list'),

    path('clientassignment_rud/<int:pk>/' , ClientEmployeeAssignmentRUDView.as_view() , name='clientassignment_rud' ),
    path('clientassignment_cl/' ,ClientEmployeeAssignmentCreateView.as_view() , name = 'clientassignment_cl'),
    path('clientassignment_list/<int:client>/' ,ClientEmployeeAssignmentListView.as_view() , name = 'clientassignment_list'),

    # path('assignments/create/', ClientEmployeeAssignmentCreateView.as_view(), name='assignment-create'),
    # path('assignments/<int:pk>/', ClientEmployeeAssignmentRUDView.as_view(), name='assignment-detail'),
    # path('clients/<int:client_id>/assignments/', ClientEmployeeAssignmentListView.as_view(), name='client-assignment-list'),




]