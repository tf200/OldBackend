from rest_framework import generics
from rest_framework.response import Response

from client.pagination import CustomPagination
from system.models import Notification

from .serializers import NotificationSerialize


class NotificationList(generics.ListAPIView):
    serializer_class = NotificationSerialize
    queryset = Notification.objects.all()
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(receiver=request.user).all()
        serializer = NotificationSerialize(notifications, many=True)
        return Response(serializer.data)
