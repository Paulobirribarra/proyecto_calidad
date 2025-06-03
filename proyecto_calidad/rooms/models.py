"""
Modelos para la gestión de salas de estudio y reservas.

Este módulo contiene los modelos Room, Reservation y Review
para el sistema de gestión de salas de estudio inteligentes.

REQ-003: Gestión de salas de estudio
REQ-004: Sistema de reservas
REQ-005: Sistema de calificaciones y feedback
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time, timedelta
import logging
import pytz

User = get_user_model()
logger = logging.getLogger(__name__)


class Room(models.Model):
    """
    Modelo para representar una sala de estudio.
    
    Attributes:
        name (str): Nombre de la sala
        description (str): Descripción detallada de la sala
        capacity (int): Capacidad máxima de personas
        equipment (str): Equipamiento disponible
        location (str): Ubicación física de la sala
        is_active (bool): Si la sala está disponible para reservas
        hourly_rate (decimal): Tarifa por hora (opcional)
        room_type (str): Tipo de sala para control de permisos
        allowed_roles (str): Roles que pueden reservar esta sala
    """
    
    ROOM_TYPE_CHOICES = (
        ('aula', 'Aula'),
        ('sala_estudio', 'Sala de Estudio'),
        ('sala_individual', 'Sala Individual'),
        ('sala_reunion', 'Sala de Reuniones'),
        ('laboratorio', 'Laboratorio'),
        ('auditorio', 'Auditorio'),
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre único de la sala"
    )
    
    description = models.TextField(
        help_text="Descripción detallada de la sala y sus características"
    )
    
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Capacidad máxima de personas"
    )
    
    equipment = models.TextField(
        blank=True,
        help_text="Equipamiento disponible (proyector, pizarra, etc.)"
    )
    
    location = models.CharField(
        max_length=200,
        help_text="Ubicación física de la sala"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la sala está disponible para reservas"
    )
    
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Tarifa por hora (0.00 = gratuita)"
    )
    
    # Configuración de horarios
    opening_time = models.TimeField(
        default=time(8, 0),
        help_text="Hora de apertura de la sala"
    )
    
    closing_time = models.TimeField(
        default=time(22, 0),
        help_text="Hora de cierre de la sala"
    )
    
    # Tipos de sala y permisos
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default='sala_estudio',
        help_text="Tipo de sala"
    )
    
    allowed_roles = models.CharField(
        max_length=255,
        default='admin,profesor,estudiante',
        help_text="Roles permitidos para reservar esta sala (separados por comas)"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_rooms'
    )
    
    def __str__(self):
        """Representación string de la sala."""
        return f"{self.name} (Cap: {self.capacity})"
    
    @property
    def average_rating(self):
        """
        Calcula la calificación promedio de la sala.
        
        Returns:
            float: Promedio de calificaciones o 0 si no hay reviews
        """
        # Obtener reviews a través de las reservations
        from django.db.models import Avg
        avg = self.reservations.filter(review__isnull=False).aggregate(
            avg_rating=Avg('review__rating')
        )['avg_rating']
        
        if avg:
            return round(avg, 1)
        return 0
    @property
    def total_reviews(self):
        """Retorna el número total de reviews."""
        return self.reservations.filter(review__isnull=False).count()
    
    @property
    def review_count(self):
        """Alias para template compatibility."""
        return self.total_reviews
    
    def get_equipment_list(self):
        """Retorna una lista del equipamiento disponible."""
        if not self.equipment:
            return []
        return [item.strip() for item in self.equipment.split(',')]
    
    @property
    def is_available_now(self):
        """Verifica si la sala está disponible en este momento."""
        now_utc = timezone.now()
        
        # Convertir a hora de Chile
        chile_tz = pytz.timezone('America/Santiago')
        now_chile = now_utc.astimezone(chile_tz)
        
        # Verificar si está dentro del horario de operación usando hora de Chile
        if now_chile.time() < self.opening_time or now_chile.time() > self.closing_time:
            return False
        
        # Verificar si hay reservas activas (las reservas se guardan en UTC)
        active_reservations = self.reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__lte=now_utc,
            end_time__gt=now_utc
        )
        
        return not active_reservations.exists()
    
    def is_available_at(self, start_time, end_time):
        """
        Verifica si la sala está disponible en un horario específico.
        
        Args:
            start_time (datetime): Hora de inicio
            end_time (datetime): Hora de fin
            
        Returns:
            bool: True si está disponible
        """
        if not self.is_active:
            return False
        
        # Verificar horarios de operación
        if (start_time.time() < self.opening_time or 
            end_time.time() > self.closing_time):
            return False
        
        # Verificar conflictos con reservas existentes
        overlapping_reservations = self.reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        return not overlapping_reservations.exists()
    
    def can_be_reserved_by(self, user):
        """
        Verifica si la sala puede ser reservada por un usuario específico
        según su rol.
        
        Args:
            user: El usuario que intenta reservar
            
        Returns:
            bool: True si el usuario puede reservar esta sala
        """
        if not user.is_authenticated:
            return False
        
        if user.is_staff or user.is_superuser:
            return True
            
        # Si el usuario es admin o profesor, puede reservar cualquier sala
        if hasattr(user, 'is_admin') and user.is_admin():
            return True
            
        if hasattr(user, 'is_profesor') and user.is_profesor():
            return True
          # Verificar si el rol del usuario está en los roles permitidos
        allowed = self.allowed_roles.split(',')
        
        if hasattr(user, 'role') and user.role in allowed:
            # Restricciones específicas para estudiantes
            if hasattr(user, 'is_estudiante') and user.is_estudiante():
                # Los estudiantes solo pueden reservar salas de estudio y salas individuales
                if self.room_type in ['sala_estudio', 'sala_individual', 'auditorio']:
                    return True
                return False
            
            # Restricciones para soporte técnico
            if hasattr(user, 'role') and user.role == 'soporte':
                # Soporte puede reservar laboratorios, salas de reuniones y auditorios
                if self.room_type in ['laboratorio', 'sala_reunion', 'auditorio']:
                    return True
                return False
                
            # Para otros roles permitidos
            return True
        
        return False
    
    def clean(self):
        """Validación personalizada del modelo."""
        super().clean()
        
        if self.opening_time >= self.closing_time:
            raise ValidationError(
                "La hora de apertura debe ser anterior a la hora de cierre"
            )
        
        if self.capacity <= 0:
            raise ValidationError("La capacidad debe ser mayor a 0")
    
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        ordering = ['name']


class Reservation(models.Model):
    """
    Modelo para representar una reserva de sala.
    
    Attributes:
        room (Room): Sala reservada
        user (User): Usuario que hizo la reserva
        start_time (datetime): Hora de inicio de la reserva
        end_time (datetime): Hora de fin de la reserva
        purpose (str): Propósito de la reserva
        status (str): Estado de la reserva
        attendees_count (int): Número de asistentes
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No se presentó'),
    ]
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    
    start_time = models.DateTimeField(
        help_text="Fecha y hora de inicio de la reserva"
    )
    
    end_time = models.DateTimeField(
        help_text="Fecha y hora de fin de la reserva"
    )
    
    purpose = models.CharField(
        max_length=200,
        help_text="Propósito o motivo de la reserva"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    attendees_count = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Número de personas que asistirán"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre la reserva"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """Representación string de la reserva."""
        return f"{self.room.name} - {self.user.username} ({self.start_time.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def duration_hours(self):
        """Calcula la duración en horas de la reserva."""
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600
    
    @property
    def total_cost(self):
        """Calcula el costo total de la reserva."""
        return float(self.room.hourly_rate) * self.duration_hours
    
    def can_be_cancelled(self):
        """
        Verifica si la reserva puede ser cancelada.
        
        Returns:
            bool: True si puede ser cancelada
        """
        if self.status in ['cancelled', 'completed', 'no_show']:
            return False
        # Permitir cancelación hasta 1 hora antes        return timezone.now() < (self.start_time - timedelta(hours=1))
    
    def update_status_if_needed(self):
        """
        Actualiza el estado de la reserva basado en la hora actual.
        
        Si la hora de finalización ya pasó y el estado es 'confirmed',
        cambia el estado a 'completed'.
        
        Returns:
            bool: True si se actualizó el estado
        """
        now = timezone.now()
        
        if self.status == 'confirmed' and now > self.end_time:
            self.status = 'completed'
            self.save(update_fields=['status'])
            logger.info(f"Reserva #{self.id} actualizada automáticamente a 'completed'")
            return True
        
        return False
    
    def can_be_reviewed(self):
        """
        Verifica si la reserva puede ser calificada.
        
        Returns:
            bool: True si puede ser calificada
        """        # Actualizar el estado si es necesario antes de verificar
        self.update_status_if_needed()
        
        return (self.status == 'completed' and
                not hasattr(self, 'review'))
    
    def clean(self):
        """Validación personalizada del modelo."""
        super().clean()
        
        # Validar que ambas fechas estén presentes antes de compararlas
        if self.start_time and self.end_time:
            # Validar que end_time sea posterior a start_time
            if self.end_time <= self.start_time:
                raise ValidationError(
                    "La hora de fin debe ser posterior a la hora de inicio"
                )
            
            # Validar duración mínima y máxima (solo si ambas fechas están presentes)
            duration = self.end_time - self.start_time
            if duration < timedelta(minutes=30):
                raise ValidationError(
                    "La duración mínima de una reserva es 30 minutos"
                )
            
            if duration > timedelta(hours=8):
                raise ValidationError(
                    "La duración máxima de una reserva es 8 horas"
                )
        
        # Validar que la reserva no sea en el pasado (solo para nuevas reservas)
        if self.start_time and not self.pk and self.start_time <= timezone.now():
            raise ValidationError(
                "No se pueden hacer reservas en el pasado"
            )
        
        # Validar capacidad
        if self.room and self.attendees_count > self.room.capacity:
            raise ValidationError(
                f"El número de asistentes ({self.attendees_count}) "
                f"excede la capacidad de la sala ({self.room.capacity})"
            )
        
        # Validar disponibilidad de la sala
        if self.room and self.start_time and self.end_time:
            if not self.room.is_available_at(self.start_time, self.end_time):
                # Excluir la reserva actual si estamos editando
                exclude_id = self.pk if self.pk else None
                if exclude_id:
                    overlapping = self.room.reservations.filter(
                        status__in=['confirmed', 'in_progress'],
                        start_time__lt=self.end_time,
                        end_time__gt=self.start_time
                    ).exclude(pk=exclude_id)
                else:
                    overlapping = self.room.reservations.filter(
                        status__in=['confirmed', 'in_progress'],
                        start_time__lt=self.end_time,
                        end_time__gt=self.start_time
                    )
                
                if overlapping.exists():
                    raise ValidationError(
                        "La sala no está disponible en el horario seleccionado"
                    )
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-start_time']


class Review(models.Model):
    """
    Modelo para representar una reseña/calificación de sala.
    
    Attributes:
        reservation (Reservation): Reserva asociada
        rating (int): Calificación de 1 a 5
        comment (str): Comentario opcional
        cleanliness_rating (int): Calificación de limpieza
        equipment_rating (int): Calificación del equipamiento
        comfort_rating (int): Calificación de comodidad
        comment_type (str): Tipo de comentario (elogio, sugerencia, problema)
    """
    
    COMMENT_TYPE_CHOICES = [
        ('positive', 'Comentario Positivo'),
        ('suggestion', 'Sugerencia de Mejora'),
        ('problem', 'Reporte de Problema'),
        ('neutral', 'Comentario General'),
    ]
    
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='review'
    )
    
    # Calificación general
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación general de 1 a 5 estrellas"
    )
    
    # Calificaciones específicas
    cleanliness_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de limpieza de 1 a 5"
    )
    
    equipment_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación del equipamiento de 1 a 5"
    )
    
    comfort_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de comodidad de 1 a 5"
    )
    
    comment = models.TextField(
        blank=True,
        max_length=1000,
        help_text="Comentario opcional sobre la experiencia"
    )
    
    comment_type = models.CharField(
        max_length=20,
        choices=COMMENT_TYPE_CHOICES,
        default='neutral',
        help_text="Tipo de comentario para categorización"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """Representación string de la reseña."""
        return f"Review {self.reservation.room.name} - {self.rating}★"
    
    @property
    def room(self):
        """Acceso directo a la sala."""
        return self.reservation.room
    
    @property
    def user(self):
        """Acceso directo al usuario."""
        return self.reservation.user
    
    @property
    def average_specific_rating(self):
        """Calcula el promedio de las calificaciones específicas."""
        return round(
            (self.cleanliness_rating + self.equipment_rating + self.comfort_rating) / 3,
            1
        )
    
    def clean(self):
        """Validación personalizada del modelo."""
        super().clean()
        
        # Solo validar si ya tenemos una reserva asignada
        if self.reservation_id:
            # Validar que la reserva esté completada
            if self.reservation.status != 'completed':
                raise ValidationError(
                    "Solo se pueden calificar reservas completadas"
                )
            
            # Log de nueva reseña
            logger.info(
                f"Nueva reseña creada para {self.reservation.room.name} "
                f"por {self.reservation.user.username} - Rating: {self.rating}"
            )
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-created_at']
