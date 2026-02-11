import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from chat.models import Chat, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("🔥 WebSocket connect attempt")

        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self.is_chat_member():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = (data.get('message') or '').strip()
        if not message:
            return

        # Save message to database
        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'sender_id': self.user.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
        }))

    @database_sync_to_async
    def is_chat_member(self):
        return Chat.objects.filter(id=self.chat_id).filter(
            Q(user1=self.user) | Q(user2=self.user)
        ).exists()

    @database_sync_to_async
    def save_message(self, message):
        chat = Chat.objects.get(id=self.chat_id)
        Message.objects.create(
            chat=chat,
            sender=self.user,
            content=message
        )
