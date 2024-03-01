from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from .models import Conversation , Message
from .serializers import ConversationSerializer , MessageSerializer

class UserConversationsAPIView(ListAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        # Get the user from the request
        user = self.request.user.id
        # Return conversations involving the authenticated user
        return Conversation.objects.filter(involved=user)


class ConversationMessagesAPIView(ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs['conv_id']
        return Message.objects.filter(conversation__id=conversation_id).order_by('timestamp')