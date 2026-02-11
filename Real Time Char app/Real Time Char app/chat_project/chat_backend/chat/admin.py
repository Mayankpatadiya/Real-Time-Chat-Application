from django.contrib import admin
from .models import Chat, UserProfile, ChatGroup

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ChatGroup)
admin.site.register(Chat)