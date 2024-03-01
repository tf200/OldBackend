from django.db import models
from authentication.models import CustomUser
import uuid
# Create your models here.



class Conversation(models.Model):
    involved = models.ManyToManyField(CustomUser, related_name='conversations')
    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        # Find existing conversation between the two users
        conversation = cls.objects.filter(involved=user1).filter(involved=user2).first()
        if conversation:
            # If existing conversation, return it with 'created' as False
            return conversation, False
        else:
            # If no existing conversation, create a new one
            conversation = cls.objects.create()
            conversation.involved.add(user1, user2)
            # Return the new conversation with 'created' as True
            return conversation, True




class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)