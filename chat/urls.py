from django.urls import path
from .views import UserConversationsAPIView, ConversationMessagesAPIView , get_conversation_messages , ConversationLookupView

urlpatterns = [
    path('conversations/', UserConversationsAPIView.as_view(), name='user-conversations'),
    path('messages/<int:conv_id>/', get_conversation_messages, name='conversation_messages'),
    path('conversation/lookup/', ConversationLookupView.as_view(), name='conversation-lookup'),
]