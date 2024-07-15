"""
URL configuration for healty project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("authentication.urls")),
    path("client/", include("client.urls")),
    path("employee/", include("employees.urls")),
    path("ad/", include("adminmodif.urls")),
    path("appointments/", include("planning.urls")),
    path("chat/", include("chat.urls")),
    path("", api.urls),
]

# Add static and media files
# For media & assets
urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))  # type: ignore
urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))  # type: ignore
