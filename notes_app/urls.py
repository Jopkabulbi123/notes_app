from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from notes.views import custom_login_view
from notes.views import register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notes.urls')),
    path('accounts/login/', custom_login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', register, name='register'),
]