"""
Configuración del panel de administración para usuarios.

REQ-002: Panel de administración para gestión de usuarios
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del admin para CustomUser.
    
    Extiende UserAdmin para incluir los campos personalizados.
    """
    
    # Campos a mostrar en la lista
    list_display = (
        'username', 
        'email', 
        'role', 
        'is_active', 
        'date_joined',
        'email_notifications'
    )
    
    # Filtros laterales
    list_filter = (
        'role', 
        'is_active', 
        'is_staff', 
        'email_notifications',
        'date_joined'
    )
    
    # Campos de búsqueda
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Ordenamiento por defecto
    ordering = ('-date_joined',)
    
    # Campos editables en línea
    list_editable = ('role', 'is_active')
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': (
                'role', 
                'phone_number', 
                'email_notifications',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('created_at', 'updated_at')
    
    # Configuración para formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': (
                'email',
                'role', 
                'phone_number', 
                'email_notifications'
            ),
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related()
    
    def save_model(self, request, obj, form, change):
        """Logging personalizado al guardar usuarios."""
        action = "actualizado" if change else "creado"
        super().save_model(request, obj, form, change)
        
        # Log de la acción
        self.message_user(
            request, 
            f'Usuario {obj.username} {action} exitosamente.'
        )
