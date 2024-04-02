import json
import uuid
from urllib.parse import parse_qs

import jwt
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken

from authentication.models import CustomUser

from .models import Conversation, Message


class WsConnection(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = str(uuid.uuid4())
        # Extract token from the query string
        query_string = parse_qs(self.scope["query_string"].decode("utf8"))
        token = query_string.get("token", [None])[0]

        if not token:
            await self.close()
            return

        # Validate the JWT and retrieve the user
        user = await self.get_user_from_token(token)

        if user:
            # Add the user's connection to their unique group
            self.user_id = user.id
            self.room_group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            # Store the user ID in the cache (your existing code)

            await self.accept()
        else:
            await self.close()

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Get the user from the decoded token
            user_id = payload.get("user_id")
            if not user_id:
                return None
            return CustomUser.objects.get(id=user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, CustomUser.DoesNotExist) as e:
            return None

    async def disconnect(self, close_code):
        # You can add cleanup logic here if needed
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get("message")
            message_id = text_data_json.get("message_id")  # UUID sent from the frontend
            recipient_id = text_data_json.get("recipient_id")
            conversation_id = text_data_json.get("conv_id", None)
            sender_id = self.user_id

            if not conversation_id:  # If conv_id is empty, create or get conversation
                conversation = await self.create_or_get_conversation(sender_id, recipient_id)
            else:  # Existing conversation
                conversation = await self.get_conversation_by_id(conversation_id)
                if not conversation or not await self.is_sender_part_of_conversation(
                    sender_id, conversation.id
                ):
                    # Handle error: conversation does not exist or sender is not part of it
                    return

            if conversation:

                # Save the message and get its UUID
                saved_message_id, conv_id, timestamp = await self.save_message(
                    message_id, sender_id, conversation.id, message_content
                )

                await self.forward_message(
                    recipient_id, message_content, conversation.id, sender_id, timestamp
                )
                # Send confirmation back to the sender
                await self.send(
                    text_data=json.dumps(
                        {
                            "conversation": conv_id,
                            "type": "message_delivery",
                            "status": "success",
                            "message_id": str(
                                saved_message_id
                            ),  # Send back the UUID of the saved message
                            "info": "Message successfully sent and stored",
                        }
                    )
                )

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
    def save_message(self, message_id, sender_id, conversation_id, content):

        sender = CustomUser.objects.get(id=sender_id)

        conversation = Conversation.objects.get(id=conversation_id)
        # Use the provided UUID from the frontend as the message ID
        message = Message.objects.create(
            id=message_id, sender=sender, conversation=conversation, content=content
        )
        print(message.timestamp)
        return message.id, conversation.id, message.timestamp

    async def forward_message(self, recipient_id, message, conversation_id, sender_id, timestamp):
        # Construct the group name based on recipient ID

        group_name = f"user_{recipient_id}"

        # Sending the message to the recipient's group with sender_id included
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "chat_message",
                "content": message,
                "conversation_id": conversation_id,
                "sender": sender_id,
                "timestamp": f"{timestamp}",
            },
        )

    # Handler for sending chat messages
    async def chat_message(self, event):
        # Send the actual message along with sender_id
        await self.send(
            text_data=json.dumps(
                {
                    "type": "sent_message",
                    "message": event["content"],  # Use 'content' instead of 'message'
                    "conversation_id": event["conversation_id"],
                    "sender_id": event["sender"],  # Use 'sender' instead of 'sender_id'
                    "timestamp": event[
                        "timestamp"
                    ],  # Optionally forward the timestamp to the client
                }
            )
        )
