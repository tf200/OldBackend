from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import GroupMembership
from authentication.models import CustomUser

class AssignGroupSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    group_id = serializers.IntegerField()
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

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

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date is not None and end_date is not None:
            if start_date >= end_date:
                raise serializers.ValidationError("End date must be greater than start date")
        return data




class GroupSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']

    def get_user_count(self, obj):
        # Count the number of users in this group
        count = GroupMembership.objects.filter(group=obj).count()
        return count