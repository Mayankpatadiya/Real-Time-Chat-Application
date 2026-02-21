import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.utils import timezone
from chat.models import Chat, Message, ChatGroup, UserProfile

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

        # Update user's last_seen timestamp
        await self.update_user_presence()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        # Update user's last_seen timestamp on disconnect
        await self.update_user_presence()
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        # Handle typing events
        if 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_message',
                    'typing': data['typing'],
                    'sender': self.user.username,
                    'sender_id': self.user.id,
                }
            )
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
            'type': 'chat_message',
            'message': event.get('message', ''),
            'file_url': event.get('file_url'),
            'file_name': event.get('file_name'),
            'message_type': event.get('message_type', 'text'),
            'sender': event['sender'],
            'sender_id': event['sender_id'],
        }))

    async def typing_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'typing': event['typing'],
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
    
    @database_sync_to_async
    def update_user_presence(self):
        try:
            user_profile = UserProfile.objects.get(user=self.user)
            user_profile.last_seen = timezone.now()
            user_profile.save(update_fields=['last_seen'])
        except UserProfile.DoesNotExist:
            pass


class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'group_{self.group_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self.is_group_member():
            await self.close()
            return

        # Update user's last_seen timestamp
        await self.update_user_presence()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Update user's last_seen timestamp on disconnect
        await self.update_user_presence()
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        # Handle typing events
        if 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_message',
                    'typing': data['typing'],
                    'sender': self.user.username,
                    'sender_id': self.user.id,
                }
            )
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
            'type': 'chat_message',
            'message': event.get('message', ''),
            'file_url': event.get('file_url'),
            'file_name': event.get('file_name'),
            'message_type': event.get('message_type', 'text'),
            'sender': event['sender'],
            'sender_id': event['sender_id'],
        }))

    async def typing_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'typing': event['typing'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
        }))

    @database_sync_to_async
    def is_group_member(self):
        try:
            group = ChatGroup.objects.get(id=self.group_id)
            return group.members.filter(user=self.user).exists() or group.created_by.user == self.user
        except ChatGroup.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message):
        group = ChatGroup.objects.get(id=self.group_id)
        Message.objects.create(
            group=group,
            sender=self.user,
            content=message
        )
    
    @database_sync_to_async
    def update_user_presence(self):
        try:
            user_profile = UserProfile.objects.get(user=self.user)
            user_profile.last_seen = timezone.now()
            user_profile.save(update_fields=['last_seen'])
        except UserProfile.DoesNotExist:
            pass
