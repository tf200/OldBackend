from django.urls import path 
# from .views import register_user, login_user , CreateProjectView , UpdateProjectView , FileUploadView, ProjectDeleteView ,UserProjectsListView 

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomTokenObtainPairView , LocationCreateAPIView



urlpatterns = [
     path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('locations/', LocationCreateAPIView.as_view(), name='location-create'),


]