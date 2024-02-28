from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from authentication.models import CustomUser
from .models import Message , Conversation
from urllib.parse import parse_qs
import json
import jwt



class WsConnection(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from the query string
        query_string = parse_qs(self.scope['query_string'].decode('utf8'))
        token = query_string.get('token', [None])[0]

        if not token:
            await self.close()
            return

        # Validate the JWT and retrieve the user
        user = await self.get_user_from_token(token)

        if user:
            # Store the user ID in the cache
            await self.store_user_id_in_cache(user.id)
            await self.accept()
        else:
            await self.close()

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Get the user from the decoded token
            user_id = payload.get('user_id')
            if not user_id:
                return None
            return CustomUser.objects.get(id=user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, CustomUser.DoesNotExist) as e:
            return None


    @database_sync_to_async
    def store_user_id_in_cache(self, user_id):
        # Use the user ID as the key to store in the cache
        cache.set("websocket_session_token", user_id, timeout=3600)  # Cache timeout of 1 hour

    async def disconnect(self, close_code):
        # You can add cleanup logic here if needed
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get('message')
            recipient_id = text_data_json.get('recipient_id')
            conversation_id = text_data_json.get('conv_id', None)
            
            sender_id = cache.get("websocket_session_token")
            
            
            
            if not conversation_id:  # If conv_id is empty, create a new conversation
                conversation = await self.create_or_get_conversation(sender_id, recipient_id)
                
            else:  # Existing conversation
                conversation = await self.get_conversation_by_id(conversation_id)
                if not conversation or not await self.is_sender_part_of_conversation(sender_id, conversation.id):
                    # Handle error: conversation does not exist or sender is not part of it
                    return
            
            if conversation:
                # Save the message
                await self.save_message(sender_id, conversation.id, message_content)
                # Forward the message
                await self.forward_message(recipient_id, message_content, conversation.id , sender_id )

    @database_sync_to_async
    def create_or_get_conversation(self, sender_id, recipient_id):
        sender = CustomUser.objects.get(id=sender_id)
        recipient = CustomUser.objects.get(id=recipient_id)
        conversation, created = Conversation.get_or_create_conversation(sender, recipient)
        return conversation

    @database_sync_to_async
    def get_conversation_by_id(self, conversation_id):
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender_id, conversation_id, content):
        sender = CustomUser.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=conversation_id)
        message = Message.objects.create(sender=sender, conversation=conversation, content=content)
        return message


    async def forward_message(self, recipient_id, message, conversation_id, sender_id):
        # Construct the group name based on recipient ID
        group_name = f'user_{recipient_id}'

        # Sending the message to the recipient's group with sender_id included
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'message': message,
                'conversation_id': conversation_id,
                'sender_id': sender_id,  # Include sender_id in the event message
            }
        )

    # Handler for sending chat messages
    async def chat_message(self, event):
        # Send the actual message along with sender_id
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'conversation_id': event['conversation_id'],
            'sender_id': event['sender_id'],  # Forward sender_id to the client
        }))