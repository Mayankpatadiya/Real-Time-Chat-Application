from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        
        return self.user.username
    
    def is_online(self):
        from django.utils import timezone
        from datetime import timedelta
        if self.last_seen:
            return timezone.now() - self.last_seen < timedelta(minutes=5)
        return False


class ChatGroup(models.Model):
    name = models.CharField(max_length=150)
    members = models.ManyToManyField(UserProfile, related_name='groups', blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user1', 'user2'],
                name='unique_private_chat'
            )
        ]



class Message(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.message_type == 'text':
            return f"{self.sender}: {self.content[:20]}"
        return f"{self.sender}: {self.message_type} file"
