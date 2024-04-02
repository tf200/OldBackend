# myapp/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/", consumers.WsConnection.as_asgi()),
]
