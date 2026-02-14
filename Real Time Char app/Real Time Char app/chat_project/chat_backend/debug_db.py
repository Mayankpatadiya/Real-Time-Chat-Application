import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_backend.settings')
django.setup()

from chat.models import ChatGroup, UserProfile
from django.contrib.auth.models import User

print("--- Users ---")
for u in User.objects.all():
    print(f"User: {u.username} (ID: {u.id})")
    try:
        up = UserProfile.objects.get(user=u)
        print(f"  Profile ID: {up.id}")
    except UserProfile.DoesNotExist:
        print("  NO PROFILE")

print("\n--- Groups ---")
for g in ChatGroup.objects.all():
    print(f"Group: {g.name} (ID: {g.id})")
    print(f"  Created By: {g.created_by.user.username if g.created_by else 'None'}")
    print("  Members:")
    for m in g.members.all():
        print(f"    - {m.user.username} (Profile ID: {m.id})")
