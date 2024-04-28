from rest_framework import serializers

from system.models import Notification , AttachmentFile


class NotificationSerialize(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = ["receiver"]


class AttchementFileSerialize(serializers.ModelSerializer) :
    class Meta:
        model = AttachmentFile
        fields = "__all__"