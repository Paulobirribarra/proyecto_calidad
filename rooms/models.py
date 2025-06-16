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
        location (str): Ubicación física de la sala        is_active (bool): Si la sala está disponible para reservas
        hourly_rate (decimal): Tarifa por hora (opcional)
        room_type (str): Tipo de sala para control de permisos
        allowed_roles (str): Roles que pueden reservar esta sala
    """
    
    ROOM_TYPE_CHOICES = (
        ('aula', 'Aula'),
        ('laboratorio_ciencias', 'Laboratorio de Ciencias'),
        ('laboratorio_informatica', 'Laboratorio de Informática'),
        ('biblioteca', 'Biblioteca'),
        ('sala_profesores', 'Sala de Profesores'),
        ('auditorio', 'Auditorio'),
        ('equipamiento', 'Equipamiento/Recurso'),
        ('sala_reunion', 'Sala de Reuniones'),
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
        help_text="Tarifa por hora (0.00 = gratuita)"    )
    
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
        max_length=30,
        choices=ROOM_TYPE_CHOICES,
        default='aula',
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
    
    def get_detailed_availability_status(self):
        """
        Retorna información detallada sobre el estado de disponibilidad.
        Proporciona contexto temporal más específico que el simple estado binario.
        """
        if not self.is_open_now:
            return {
                'status': 'closed',
                'message': 'Sala cerrada por horario',
                'context': 'closed'
            }
        
        now_utc = timezone.now()
        
        # Obtener reservas activas
        active_reservations = self.reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__lte=now_utc,
            end_time__gt=now_utc
        )
        
        if active_reservations.exists():
            # Encontrar la reserva que termina más tarde
            current_reservation = active_reservations.order_by('end_time').last()
            
            # Verificar si hay más reservas después hoy
            next_reservations = self.reservations.filter(
                status__in=['confirmed', 'in_progress'],
                start_time__gt=current_reservation.end_time,
                start_time__date=now_utc.date()
            ).order_by('start_time')
            
            if next_reservations.exists():
                next_reservation = next_reservations.first()
                gap_duration = next_reservation.start_time - current_reservation.end_time
                # Si hay menos de 15 minutos entre reservas, considerarlo como ocupado continuo
                if gap_duration.total_seconds() < 900:  # 15 minutos
                    message = f"Ocupada hasta las {next_reservation.end_time.strftime('%H:%M')}"
                else:
                    message = f"Ocupada hasta las {current_reservation.end_time.strftime('%H:%M')}, luego disponible"
            else:
                message = f"Ocupada hasta las {current_reservation.end_time.strftime('%H:%M')}, luego disponible"
            
            return {
                'status': 'occupied',
                'message': message,
                'context': 'partial_occupied',
                'next_available': current_reservation.end_time,
                'current_reservation': current_reservation
            }
        else:
            # Verificar próximas reservas hoy
            today_reservations = self.reservations.filter(
                status__in=['confirmed', 'in_progress'],
                start_time__date=now_utc.date(),
                start_time__gt=now_utc
            ).order_by('start_time')
            if today_reservations.exists():
                next_reservation = today_reservations.first()
                time_until_next = next_reservation.start_time - now_utc
                
                if time_until_next.total_seconds() < 3600:  # Menos de 1 hora
                    minutes_until = int(time_until_next.total_seconds() / 60)
                    message = f"Disponible por {minutes_until} minutos (próxima reserva a las {next_reservation.start_time.strftime('%H:%M')})"
                else:
                    message = f"Disponible hasta las {next_reservation.start_time.strftime('%H:%M')}"
                
                return {
                    'status': 'available',
                    'message': message,
                    'context': 'available_with_upcoming',
                    'next_occupied': next_reservation.start_time
                }
            else:
                return {
                    'status': 'available',
                    'message': 'Disponible por el resto del día',
                    'context': 'fully_available'
                }
    
    def get_daily_occupation_percentage(self, date=None):
        """
        Calcula el porcentaje de ocupación de la sala para un día específico.
        Útil para mostrar qué tan ocupada está realmente la sala.
        """
        if date is None:
            date = timezone.now().date()
        
        # Obtener horarios de apertura para este día
        opening_hours = self.get_opening_hours(date)
        if not opening_hours:
            return 0
        
        # Calcular total de horas operativas
        total_operational_minutes = 0
        for opening_hour in opening_hours:
            start_dt = timezone.make_aware(
                timezone.datetime.combine(date, opening_hour.start_time)
            )
            end_dt = timezone.make_aware(
                timezone.datetime.combine(date, opening_hour.end_time)
            )
            total_operational_minutes += (end_dt - start_dt).total_seconds() / 60
        
        if total_operational_minutes == 0:
            # Si no hay horarios específicos, usar horarios generales de la sala
            start_dt = timezone.make_aware(
                timezone.datetime.combine(date, self.opening_time)
            )
            end_dt = timezone.make_aware(
                timezone.datetime.combine(date, self.closing_time)
            )
            total_operational_minutes = (end_dt - start_dt).total_seconds() / 60
        
        if total_operational_minutes == 0:
            return 0
        
        # Calcular minutos ocupados por reservas
        occupied_minutes = 0
        day_reservations = self.reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__date=date
        )
        
        for reservation in day_reservations:
            # Calcular intersección con horarios de apertura
            reservation_start = max(
                reservation.start_time,
                timezone.make_aware(timezone.datetime.combine(date, self.opening_time))
            )
            reservation_end = min(
                reservation.end_time,
                timezone.make_aware(timezone.datetime.combine(date, self.closing_time))
            )
            
            if reservation_start < reservation_end:
                occupied_minutes += (reservation_end - reservation_start).total_seconds() / 60
        
        return min(100, (occupied_minutes / total_operational_minutes) * 100)
    
    @property
    def is_open_now(self):
        """Verifica si la sala está abierta en este momento."""
        now = timezone.now()
        chile_tz = pytz.timezone('America/Santiago')
        now_chile = now.astimezone(chile_tz)
        current_time = now_chile.time()
        
        return self.opening_time <= current_time <= self.closing_time
    
    def get_opening_hours(self, date):
        """
        Obtiene los horarios de apertura para una fecha específica.
        Por ahora retorna None ya que usamos horarios fijos de la sala.
        """
        return None
    
    def can_be_reserved_by(self, user):
        """
        Verifica si la sala puede ser reservada por un usuario específico
        basándose en los roles permitidos y el tipo de sala.
        """
        if not self.is_active or not user.is_authenticated:
            return False
        
        # Los administradores y superusuarios pueden reservar cualquier sala
        if user.is_superuser or user.is_staff:
            return True
        
        # Verificar roles específicos
        if hasattr(user, 'role'):
            # Restricciones para estudiantes
            if user.role == 'estudiante':
                # Los estudiantes solo pueden reservar salas de estudio y salas individuales
                if self.room_type in ['sala_estudio', 'sala_individual', 'auditorio']:
                    return True
                return False
            
            # Restricciones para soporte técnico
            if user.role == 'soporte':
                # Soporte puede reservar laboratorios, salas de reuniones y auditorios
                if self.room_type in ['laboratorio', 'sala_reunion', 'auditorio']:
                    return True
                return False
                
            # Para otros roles permitidos
            return True
        
        return False


class Reservation(models.Model):
    """
    Modelo para representar una reserva de sala.
    
    Attributes:
        user (User): Usuario que realiza la reserva
        room (Room): Sala reservada
        start_time (datetime): Fecha y hora de inicio
        end_time (datetime): Fecha y hora de fin
        purpose (str): Propósito de la reserva
        attendees_count (int): Número de asistentes
        notes (str): Notas adicionales
        status (str): Estado de la reserva
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="Usuario que realiza la reserva"
    )
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="Sala reservada"
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
    
    attendees_count = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Número de personas que asistirán"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre la reserva"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed',
        help_text="Estado actual de la reserva"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-start_time']
    
    def __str__(self):
        """Representación string de la reserva."""
        return f"{self.room.name} - {self.user.username} ({self.start_time.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def duration_hours_rounded(self):
        """Calcula la duración en horas redondeadas."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return round(duration.total_seconds() / 3600, 1)
        return None
    
    @property
    def is_active(self):
        """Verifica si la reserva está actualmente en progreso."""
        now = timezone.now()
        return (self.status in ['confirmed', 'in_progress'] and 
                self.start_time <= now <= self.end_time)
    
    def can_be_cancelled(self):
        """Verifica si la reserva puede ser cancelada."""
        if self.status != 'confirmed':
            return False
        
        now = timezone.now()
        # Permitir cancelación hasta 30 minutos antes del inicio
        time_before_start = self.start_time - now
        return time_before_start.total_seconds() > 1800  # 30 minutos
    
    def clean(self):
        """Validaciones del modelo."""
        super().clean()
        
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")
            
            # Validar que no exceda la capacidad de la sala
            if self.attendees_count and self.room and self.attendees_count > self.room.capacity:
                raise ValidationError(
                    f"El número de asistentes ({self.attendees_count}) excede "
                    f"la capacidad de la sala ({self.room.capacity})."
                )


class Review(models.Model):
    """
    Modelo para representar una reseña de sala.
    
    Attributes:
        reservation (Reservation): Reserva asociada
        rating (int): Calificación general (1-5)
        cleanliness_rating (int): Calificación de limpieza (1-5)
        equipment_rating (int): Calificación de equipamiento (1-5)
        comfort_rating (int): Calificación de comodidad (1-5)
        comment (str): Comentario de la reseña
        comment_type (str): Tipo de comentario
    """
    
    COMMENT_TYPE_CHOICES = (
        ('positive', 'Comentario Positivo'),
        ('suggestion', 'Sugerencia de Mejora'),
        ('problem', 'Reporte de Problema'),
        ('neutral', 'Comentario General'),
    )
    
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='review',
        help_text="Reserva asociada a esta reseña"
    )
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación general de 1 a 5 estrellas"
    )
    
    cleanliness_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Calificación de limpieza de 1 a 5 estrellas"
    )
    
    equipment_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Calificación de equipamiento de 1 a 5 estrellas"
    )
    
    comfort_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Calificación de comodidad de 1 a 5 estrellas"
    )
    
    comment = models.TextField(
        blank=True,
        help_text="Comentario adicional sobre la experiencia"
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
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-created_at']
    
    def __str__(self):
        """Representación string de la reseña."""
        try:
            if hasattr(self, 'reservation_id') and self.reservation_id:
                return f"Reseña de {self.reservation.room.name} por {self.reservation.user.username} ({self.rating}★)"
            else:
                return f"Reseña (sin reserva asignada) - Rating: {self.rating}★"
        except (AttributeError, Review.reservation.RelatedObjectDoesNotExist):
            return f"Reseña (ID: {self.pk or 'nuevo'}) - Rating: {self.rating}★"
    
    def clean(self):
        """Validaciones del modelo."""
        super().clean()
        
        # Validar que la reserva esté completada (solo si reservation_id está establecido)
        if hasattr(self, 'reservation_id') and self.reservation_id:
            try:
                reservation = self.reservation
                if reservation and reservation.status != 'completed':
                    raise ValidationError("Solo se pueden crear reseñas para reservas completadas.")
            except Review.reservation.RelatedObjectDoesNotExist:
                # La reserva no está asignada todavía, saltear esta validación
                pass
        
        # Validar rangos de calificaciones
        rating_fields = ['rating', 'cleanliness_rating', 'equipment_rating', 'comfort_rating']
        for field_name in rating_fields:
            value = getattr(self, field_name, None)
            if value is not None and (value < 1 or value > 5):
                raise ValidationError(f"La calificación {field_name} debe estar entre 1 y 5.")
