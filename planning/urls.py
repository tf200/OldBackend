from django.urls import path

from .views import (
    AppointmentListView,
    AppointmentRUDView,
    AppointmentViewSet,
    TemporaryFileUploadView,
)

urlpatterns = [
    path(
        "create/",
        AppointmentViewSet.as_view(
            {
                "post": "create",
            }
        ),
        name="appointment-create",
    ),
    path(
        "patch/<int:pk>/",
        AppointmentViewSet.as_view(
            {
                "patch": "partial_update",  # For partial updates
                "put": "update",  # For full updates
            }
        ),
        name="appointment-update",
    ),
    path("list/", AppointmentListView.as_view(), name="appointment-list"),
    path("temporary-files/", TemporaryFileUploadView.as_view(), name="temporary_file_upload"),
    path("rud/<int:pk>/", AppointmentRUDView.as_view(), name="apointment-rud"),
]
