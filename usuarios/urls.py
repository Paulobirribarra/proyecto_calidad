"""
URLs para la gestión de usuarios.

Define las rutas para autenticación, perfil
y gestión de usuarios.

REQ-013: URLs de autenticación y perfil
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Perfil de usuario
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.user_profile_edit, name='profile_edit'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
