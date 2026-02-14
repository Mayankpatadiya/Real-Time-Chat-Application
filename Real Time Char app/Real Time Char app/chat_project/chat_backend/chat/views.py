from django.shortcuts import render , redirect
from django.db import models
from django.http import HttpResponse
from django.http import HttpRequest
from django.contrib.auth.models import User
from .models import Chat, Message
from .models import UserProfile, ChatGroup
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



# Create your views here.

def chat_room(request):
    return render(request,'chat_room.html')

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard") 
     
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        conf_pass = request.POST.get("conf_pass")
        photo = request.FILES.get("profile_photo")

        if not username or not email or not password:
            messages.error(request, "All fields are required")
            return redirect("register")

        if password != conf_pass:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")
        
        try:
            validate_password(password, user=None)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("register")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            profile_photo=photo
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "register.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard") 
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")
@login_required(login_url='login')
def dashboard(request):
    users = UserProfile.objects.exclude(user=request.user).order_by('id')
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        groups = ChatGroup.objects.filter(models.Q(members=user_profile) | models.Q(created_by=user_profile)).distinct()
    except UserProfile.DoesNotExist:
        groups = []

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            print("MESSAGE RECEIVED:", text)

    return render(request, 'dashboard.html', {
        'users': users,
        'groups': groups
    })
# ...

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        members_ids = request.POST.getlist('members')

        try:
            created_by = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
             messages.error(request, "User profile not found")
             return redirect('dashboard')

        group = ChatGroup.objects.create(
            name=name,
            created_by=created_by
        )

        if members_ids:
            group.members.set(UserProfile.objects.filter(id__in=members_ids))

        messages.success(request, 'Group created successfully')
        return redirect('dashboard')



@login_required(login_url='login')
def profile(request):
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        conf_pass = request.POST.get('conf_pass')
        profile_photo = request.FILES.get('profile_photo')

        # Update email
        if email:
            request.user.email = email
            request.user.save()

        # Update profile photo
        if profile_photo:
            user_profile.profile_photo = profile_photo
            user_profile.save()

        # Update password
        if password:
            if password != conf_pass:
                messages.error(request, 'Passwords do not match')
                return redirect('profile')
            
            try:
                validate_password(password, user=request.user)
                request.user.set_password(password)
                request.user.save()
                messages.success(request, 'Password updated. Please login again.')
                return redirect('login')
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return redirect('profile')

        messages.success(request, 'Profile updated successfully')
        return redirect('profile')

    return render(request, 'profile.html', {
        'user_profile': user_profile
    })

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        members_ids = request.POST.getlist('members')

        created_by = UserProfile.objects.get(user=request.user)

        group = ChatGroup.objects.create(
            name=name,
            created_by=created_by
        )

        if members_ids:
            group.members.set(UserProfile.objects.filter(id__in=members_ids))

        # Add the creator to the group members
        group.members.add(created_by)

        messages.success(request, 'Group created successfully')
        return redirect('dashboard')

    users = UserProfile.objects.exclude(user=request.user)
    return render(request, 'new_group.html', {'users': users})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def user_list(request):
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'user_list.html', {
        'users': users
    })
@login_required(login_url='login')
def chat_view(request, user_id):
    other_user = User.objects.get(id=user_id)

    user1, user2 = sorted([request.user, other_user], key=lambda u: u.id)

    chat, created = Chat.objects.get_or_create(
        user1=user1,
        user2=user2
    )

    if request.method == "POST":
        text = request.POST.get('message')
        if text:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=text
            )
        return redirect('chat', user_id=other_user.id)

    messages_qs = chat.messages.order_by('created_at')
    users = UserProfile.objects.exclude(user=request.user)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        groups = ChatGroup.objects.filter(models.Q(members=user_profile) | models.Q(created_by=user_profile)).distinct()
    except UserProfile.DoesNotExist:
        groups = []

    return render(request, "dashboard.html", {
        "users": users,
        "groups": groups,
        "active_user": other_user,
        "chat": chat,
        "messages": messages_qs,
    })

@login_required(login_url='login')
def group_chat_view(request, group_id):
    group = ChatGroup.objects.get(id=group_id)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('dashboard')

    # Check membership
    if user_profile not in group.members.all() and group.created_by != user_profile:
        messages.error(request, "You are not a member of this group")
        return redirect('dashboard')

    if request.method == "POST":
        text = request.POST.get('message')
        if text:
            Message.objects.create(
                group=group,
                sender=request.user,
                content=text
            )
        return redirect('group_chat', group_id=group.id)

    messages_qs = group.messages.order_by('created_at')
    
    # Context for sidebar
    users = UserProfile.objects.exclude(user=request.user)
    groups = ChatGroup.objects.filter(models.Q(members=user_profile) | models.Q(created_by=user_profile)).distinct()

    return render(request, "dashboard.html", {
        "users": users,
        "groups": groups,
        "active_group": group,
        "messages": messages_qs,
    })
