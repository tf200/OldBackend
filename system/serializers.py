from rest_framework import serializers

from system.models import Notification


class NotificationSerialize(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = ["receiver"]
