from django.urls import path
from .consumers import ChatConsumer, GroupConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi()),
    path("ws/group/<int:group_id>/", GroupConsumer.as_asgi()),
]