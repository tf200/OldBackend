from rest_framework import serializers

from authentication.models import CustomUser

from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    involved_details = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["involved_details", "id"]

    def get_involved_details(self, obj):
        # Initialize an empty list to hold the user details
        details_list = []
        # Iterate over each user involved in the conversation
        for user in obj.involved.all():
            # Directly access the EmployeeProfile associated with the user
            # Assuming the one-to-one relationship is accessible via a related_name or directly
            employee_profile = user.profile  # Adjust this based on your actual related_name
            # Construct a dict with the desired information
            user_details = {
                "id": user.id,
                "first_name": employee_profile.first_name,
                "last_name": employee_profile.last_name,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
            }
            # Append the user details dict to the list
            details_list.append(user_details)
        # Return the list of user details
        return details_list


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ["id", "sender", "conversation", "content", "timestamp", "read_status"]


class ConversationLookupSerializer(serializers.Serializer):
    involved = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,  # Assuming a conversation needs at least two users
        max_length=2,  # Adjust based on your maximum number of participants per conversation
    )

    def create(self, validated_data):
        user_ids = validated_data["involved"]
        users = CustomUser.objects.filter(id__in=user_ids)
        if users.count() == len(user_ids):  # Check if all users exist
            conversation, created = Conversation.get_or_create_conversation(*users)
            return conversation
        else:
            # Not all user IDs correspond to a valid user
            return None
