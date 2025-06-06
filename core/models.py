"""
Modelos centrales del sistema.

Este módulo contiene modelos para configuración,
logging y utilidades del sistema.

REQ-015: Configuración central del sistema
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SystemConfig(models.Model):
    """
    Configuración del sistema.
    
    Permite configurar parámetros del sistema
    desde el panel de administración.
    """
    
    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Clave de configuración"
    )
    
    value = models.TextField(
        help_text="Valor de configuración"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Descripción de la configuración"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='config_updates'
    )
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"
        ordering = ['key']


class ActivityLog(models.Model):
    """
    Log de actividades del sistema.
    
    Registra actividades importantes para
    auditoría y análisis.
    """
    
    ACTION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('register', 'Registro de usuario'),
        ('reservation_created', 'Reserva creada'),
        ('reservation_cancelled', 'Reserva cancelada'),
        ('reservation_completed', 'Reserva completada'),
        ('review_created', 'Reseña creada'),
        ('room_created', 'Sala creada'),
        ('room_updated', 'Sala actualizada'),
        ('error', 'Error del sistema'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs'
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )
    
    description = models.TextField(
        help_text="Descripción detallada de la actividad"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP del usuario"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="User agent del navegador"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        username = self.user.username if self.user else "Sistema"
        return f"{username} - {self.get_action_display()} ({self.created_at})"
    
    class Meta:
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividad"
        ordering = ['-created_at']


class ErrorLog(models.Model):
    """
    Log de errores del sistema.
    
    Registra errores para análisis y
    resolución de problemas.
    """
    
    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='error'
    )
    
    message = models.TextField(
        help_text="Mensaje de error"
    )
    
    traceback = models.TextField(
        blank=True,
        help_text="Traceback completo del error"
    )
    
    url = models.URLField(
        blank=True,
        help_text="URL donde ocurrió el error"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_logs'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    resolved = models.BooleanField(
        default=False,
        help_text="Si el error ha sido resuelto"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_level_display()}: {self.message[:100]}"
    
    class Meta:
        verbose_name = "Log de Error"
        verbose_name_plural = "Logs de Errores"
        ordering = ['-created_at']
