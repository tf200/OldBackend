from rest_framework import serializers
from django.contrib.auth.models import Group
from authentication.models import CustomUser

class AssignGroupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    group_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            CustomUser.objects.get(pk=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return value

    def validate_group_id(self, value):
        try:
            Group.objects.get(pk=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist")
        return value



from rest_framework import serializers
from django.contrib.auth.models import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']  