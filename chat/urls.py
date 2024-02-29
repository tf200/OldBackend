from django.urls import path
from .views import UserConversationsAPIView, ConversationMessagesAPIView

urlpatterns = [
    path('conversations/', UserConversationsAPIView.as_view(), name='user-conversations'),
    path('messages/<int:conv_id>/', ConversationMessagesAPIView.as_view(), name='conversation-messages'),
]