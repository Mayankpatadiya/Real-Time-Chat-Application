"""
URL configuration for chat_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from chat import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('dashboard/',views.dashboard,name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('groups/new/', views.create_group, name='create_group'),
    path('register/' ,views.register, name ='register'),
    path('login/',views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/<int:user_id>/', views.chat_view, name='chat'),
    path('group/<int:group_id>/', views.group_chat_view, name='group_chat'),
    path('upload/', views.upload_file, name='upload_file'),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
