"""
Modelos para la gestión de usuarios del sistema de salas de estudio.

Este módulo contiene el modelo CustomUser que extiende AbstractUser
para incluir roles específicos del sistema.

REQ-001: Sistema de autenticación con roles
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    
    Incluye roles específicos para el sistema de gestión de salas:
    - admin: Administrador del sistema con acceso total
    - profesor: Profesor que puede reservar cualquier tipo de sala
    - estudiante: Estudiante que puede reservar salas de estudio y salas individuales
    - soporte: Personal de soporte técnico que puede gestionar incidencias
    
    Attributes:
        role (str): Rol del usuario en el sistema
    """
    
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
        ('soporte', 'Soporte Técnico'),
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='estudiante',
        help_text="Rol del usuario en el sistema"
    )
    
    # Campos adicionales para mejor gestión
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Número de teléfono para notificaciones"
    )
    
    email_notifications = models.BooleanField(
        default=True,
        help_text="Recibir notificaciones por email"
    )
    
    terms_accepted = models.BooleanField(
        default=False,
        help_text="Términos y condiciones aceptados"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """Representación string del usuario."""
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """
        Verifica si el usuario es administrador.
        
        Returns:
            bool: True si el usuario es administrador
        """
        return self.role == 'admin'
    
    def is_profesor(self):
        """
        Verifica si el usuario es profesor.
        
        Returns:
            bool: True si el usuario es profesor
        """
        return self.role == 'profesor'
    
    def is_estudiante(self):
        """
        Verifica si el usuario es estudiante.
        
        Returns:
            bool: True si el usuario es estudiante
        """
        return self.role == 'estudiante'
    
    def is_soporte(self):
        """
        Verifica si el usuario es personal de soporte técnico.
        
        Returns:
            bool: True si el usuario es personal de soporte
        """
        return self.role == 'soporte'
    
    def can_manage_rooms(self):
        """
        Verifica si el usuario puede gestionar salas.
        
        Returns:
            bool: True si el usuario puede gestionar salas
        """
        return self.is_admin() or self.is_staff
    
    def can_reserve_any_room(self):
        """
        Verifica si el usuario puede reservar cualquier tipo de sala.
        
        Returns:
            bool: True si el usuario puede reservar cualquier sala
        """
        return self.is_admin() or self.is_profesor() or self.is_staff
    
    def clean(self):
        """
        Validación personalizada del modelo.
        
        Raises:
            ValidationError: Si hay errores de validación
        """
        super().clean()
        
        # Validar email obligatorio
        if not self.email:
            raise ValidationError("El email es obligatorio")
        
        # Log de creación/actualización
        if self.pk:
            logger.info(f"Usuario {self.username} actualizado")
        else:
            logger.info(f"Nuevo usuario creado: {self.username}")
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']
