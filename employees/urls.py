
from django.urls import path
from .views import CurrentUserProfileView

urlpatterns = [
    path('profile/', CurrentUserProfileView.as_view(), name='current-user-profile'),
]