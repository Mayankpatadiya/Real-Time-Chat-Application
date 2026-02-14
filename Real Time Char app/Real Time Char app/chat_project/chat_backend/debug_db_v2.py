import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_backend.settings')
django.setup()

from chat.models import ChatGroup, UserProfile
from django.contrib.auth.models import User

with open('db_dump.txt', 'w', encoding='utf-8') as f:
    f.write("--- Users ---\n")
    for u in User.objects.all():
        try:
            up = UserProfile.objects.get(user=u)
            f.write(f"User: {u.username} (ID: {u.id}), Profile ID: {up.id}\n")
        except UserProfile.DoesNotExist:
            f.write(f"User: {u.username} (ID: {u.id}), NO PROFILE\n")

    f.write("\n--- Groups ---\n")
    for g in ChatGroup.objects.all():
        creator = g.created_by.user.username if g.created_by else 'None'
        f.write(f"Group: {g.name} (ID: {g.id}), Created By: {creator}\n")
        f.write("  Members:\n")
        if g.members.exists():
            for m in g.members.all():
                f.write(f"    - {m.user.username} (Profile ID: {m.id})\n")
        else:
            f.write("    (No members)\n")
