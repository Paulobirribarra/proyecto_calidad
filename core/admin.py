"""
Configuración del panel de administración.

Este módulo configura el panel de administración de Django
para el módulo core del sistema.
"""

from django.contrib import admin
from .models import SystemConfig
from .reservation_security import ReservationSecurityRule, ReservationUsageLog


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """Administración de configuración del sistema."""
    
    list_display = ['key', 'value_preview', 'updated_at', 'updated_by']
    list_filter = ['updated_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def value_preview(self, obj):
        """Mostrar una vista previa del valor."""
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_preview.short_description = "Valor"
    
    def save_model(self, request, obj, form, change):
        """Guardar el usuario que actualiza la configuración."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ReservationSecurityRule)
class ReservationSecurityRuleAdmin(admin.ModelAdmin):
    """Administración de reglas de seguridad de reservas."""
    
    list_display = [
        'role', 'max_reservations_per_hour', 'max_reservations_per_day',
        'max_concurrent_reservations', 'is_active', 'updated_at'
    ]
    list_filter = ['role', 'is_active', 'enable_pattern_detection']
    search_fields = ['role']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('role', 'is_active')
        }),
        ('Límites de Frecuencia', {
            'fields': (
                'max_reservations_per_hour',
                'max_reservations_per_day',
                'max_reservations_per_week',
                'max_concurrent_reservations'
            )
        }),
        ('Límites de Duración', {
            'fields': (
                'max_total_hours_per_day',
                'max_total_hours_per_week',
                'max_advance_days'
            )
        }),
        ('Seguridad Avanzada', {
            'fields': (
                'enable_pattern_detection',
                'block_duration_minutes',
                'warning_threshold'
            )
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Asegurar que existan reglas por defecto."""
        qs = super().get_queryset(request)
        
        # Crear reglas por defecto si no existen
        try:
            from .reservation_security import initialize_default_security_rules
            initialize_default_security_rules()
        except Exception as e:
            pass
            
        return qs


@admin.register(ReservationUsageLog)
class ReservationUsageLogAdmin(admin.ModelAdmin):
    """Administración de logs de uso de reservas."""
    
    list_display = [
        'user', 'action', 'room_name', 'timestamp', 'ip_address_preview'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'room_name', 'ip_address']
    readonly_fields = [
        'user', 'action', 'reservation_id', 'room_name',
        'timestamp', 'ip_address', 'user_agent', 'additional_data'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    def ip_address_preview(self, obj):
        """Mostrar una vista previa de la IP."""
        return obj.ip_address or "N/A"
    ip_address_preview.short_description = "IP"
    
    def has_add_permission(self, request):
        """No permitir agregar logs manualmente."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir lectura de logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar logs antiguos."""
        return request.user.is_superuser
    
    actions = ['delete_old_logs']
    
    def delete_old_logs(self, request, queryset):
        """Acción para eliminar logs antiguos."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Eliminar logs de más de 90 días
        cutoff_date = timezone.now() - timedelta(days=90)
        old_logs = ReservationUsageLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        
        self.message_user(
            request,
            f"Se eliminaron {count} logs de más de 90 días."
        )
    delete_old_logs.short_description = "Eliminar logs antiguos (>90 días)"
