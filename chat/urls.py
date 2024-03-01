from django.urls import path
from .views import UserConversationsAPIView, ConversationMessagesAPIView , get_conversation_messages

urlpatterns = [
    path('conversations/', UserConversationsAPIView.as_view(), name='user-conversations'),
    path('messages/<int:conv_id>/', get_conversation_messages, name='conversation_messages'),
]