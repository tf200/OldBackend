from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    LocationCreateAPIView,
    LocationRUDAPIView,
)

# from .views import register_user, login_user , CreateProjectView , UpdateProjectView , FileUploadView, ProjectDeleteView ,UserProjectsListView


urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("locations/", LocationCreateAPIView.as_view(), name="location-create"),
    path("locations/RUD/<int:id>/", LocationRUDAPIView.as_view(), name="location-RUD"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
