"""
Sistema de Seguridad para Reservas - Prevención de Abuso

Este módulo implementa medidas de seguridad para prevenir que usuarios
malintencionados abusen del sistema de reservas realizando reservas masivas
o comportamientos no deseados.

Funcionalidades:
- Rate limiting por usuario
- Detección de patrones abusivos
- Límites configurables por rol de usuario
- Sistema de alertas automáticas
- Bloqueo temporal de usuarios abusivos
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import mail_admins
from datetime import datetime, timedelta
import logging
import json

User = get_user_model()
logger = logging.getLogger(__name__)


class ReservationSecurityRule(models.Model):
    """
    Modelo para configurar reglas de seguridad de reservas.
    
    Permite definir límites personalizados por rol de usuario
    y configurar el comportamiento del sistema de seguridad.
    """
    
    ROLE_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('admin', 'Administrador'),
        ('soporte', 'Soporte Técnico'),
        ('default', 'Por Defecto'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
        help_text="Rol de usuario al que aplica esta regla"
    )
    
    # Límites por tiempo
    max_reservations_per_hour = models.PositiveIntegerField(
        default=3,
        help_text="Máximo número de reservas por hora"
    )
    
    max_reservations_per_day = models.PositiveIntegerField(
        default=10,
        help_text="Máximo número de reservas por día"
    )
    
    max_reservations_per_week = models.PositiveIntegerField(
        default=20,
        help_text="Máximo número de reservas por semana"
    )
    
    # Límites de duración
    max_total_hours_per_day = models.PositiveIntegerField(
        default=8,
        help_text="Máximo total de horas reservadas por día"
    )
    
    max_total_hours_per_week = models.PositiveIntegerField(
        default=30,
        help_text="Máximo total de horas reservadas por semana"
    )
    
    # Límites de reservas simultáneas
    max_concurrent_reservations = models.PositiveIntegerField(
        default=3,
        help_text="Máximo número de reservas activas simultáneamente"
    )
    
    # Límites de anticipación
    max_advance_days = models.PositiveIntegerField(
        default=30,
        help_text="Máximo días de anticipación para reservar"
    )
    
    # Control de comportamiento abusivo
    enable_pattern_detection = models.BooleanField(
        default=True,
        help_text="Habilitar detección de patrones abusivos"
    )
    
    block_duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Duración del bloqueo temporal en minutos cuando se detecta abuso"
    )
    
    warning_threshold = models.FloatField(
        default=0.8,
        help_text="Umbral de advertencia (porcentaje del límite) para notificar al usuario"
    )
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Regla de Seguridad de Reserva"
        verbose_name_plural = "Reglas de Seguridad de Reservas"
    
    def __str__(self):
        return f"Reglas de seguridad para {self.get_role_display()}"


class ReservationUsageLog(models.Model):
    """
    Modelo para registrar el uso de reservas por usuario.
    
    Mantiene un historial detallado de las acciones de reserva
    para análisis de patrones y detección de abuso.
    """
    
    ACTION_CHOICES = [
        ('create', 'Crear Reserva'),
        ('cancel', 'Cancelar Reserva'),
        ('attempt_blocked', 'Intento Bloqueado'),
        ('warning_sent', 'Advertencia Enviada'),
        ('user_blocked', 'Usuario Bloqueado'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservation_usage_logs'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    reservation_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID de la reserva relacionada (si aplica)"
    )
    
    room_name = models.CharField(
        max_length=100,
        help_text="Nombre de la sala"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP del usuario"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="User Agent del navegador"
    )
    
    additional_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales en formato JSON"
    )
    
    class Meta:
        verbose_name = "Log de Uso de Reservas"
        verbose_name_plural = "Logs de Uso de Reservas"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"


class SecurityManager:
    """
    Manager principal para el sistema de seguridad de reservas.
    
    Centraliza toda la lógica de validación, detección de abuso
    y aplicación de medidas de seguridad.
    """
    
    @staticmethod
    def get_user_role(user):
        """Obtener el rol del usuario para aplicar reglas específicas."""
        if hasattr(user, 'role'):
            return user.role
        elif user.is_superuser or user.is_staff:
            return 'admin'
        else:
            return 'default'
    
    @staticmethod
    def get_security_rules(user):
        """Obtener las reglas de seguridad aplicables para un usuario."""
        user_role = SecurityManager.get_user_role(user)
        
        try:
            # Intentar obtener reglas específicas para el rol
            rules = ReservationSecurityRule.objects.get(
                role=user_role,
                is_active=True
            )
        except ReservationSecurityRule.DoesNotExist:
            try:
                # Usar reglas por defecto si no existen específicas
                rules = ReservationSecurityRule.objects.get(
                    role='default',
                    is_active=True
                )
            except ReservationSecurityRule.DoesNotExist:
                # Crear reglas por defecto si no existen
                rules = ReservationSecurityRule.objects.create(
                    role='default',
                    max_reservations_per_hour=2,
                    max_reservations_per_day=5,
                    max_reservations_per_week=15,
                    max_total_hours_per_day=6,
                    max_total_hours_per_week=25,
                    max_concurrent_reservations=2
                )
                logger.info("Creadas reglas de seguridad por defecto")
        
        return rules
    
    @staticmethod
    def is_user_blocked(user):
        """Verificar si un usuario está temporalmente bloqueado."""
        cache_key = f"reservation_block_{user.id}"
        blocked_until = cache.get(cache_key)
        
        if blocked_until and timezone.now() < blocked_until:
            return True, blocked_until
        
        return False, None
    
    @staticmethod
    def block_user_temporarily(user, duration_minutes=60, reason="Comportamiento abusivo detectado"):
        """Bloquear temporalmente a un usuario."""
        cache_key = f"reservation_block_{user.id}"
        blocked_until = timezone.now() + timedelta(minutes=duration_minutes)
        
        cache.set(cache_key, blocked_until, timeout=duration_minutes * 60)
        
        # Registrar el bloqueo
        SecurityManager.log_action(
            user=user,
            action='user_blocked',
            room_name="",
            additional_data={
                'reason': reason,
                'duration_minutes': duration_minutes,
                'blocked_until': blocked_until.isoformat()
            }
        )
        
        # Notificar a administradores
        try:
            mail_admins(
                subject=f"Usuario bloqueado temporalmente: {user.username}",
                message=f"""
                Usuario: {user.username} ({user.email})
                Razón: {reason}
                Duración: {duration_minutes} minutos
                Bloqueado hasta: {blocked_until}
                
                El usuario ha sido bloqueado automáticamente por el sistema de seguridad.
                """,
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Error enviando notificación de bloqueo: {e}")
        
        logger.warning(
            f"Usuario {user.username} bloqueado temporalmente. "
            f"Razón: {reason}. Duración: {duration_minutes} minutos"
        )
    
    @staticmethod
    def check_rate_limits(user):
        """
        Verificar si el usuario ha excedido los límites de tasa de reservas.
        
        Returns:
            tuple: (is_allowed: bool, violations: list, warnings: list)
        """
        rules = SecurityManager.get_security_rules(user)
        now = timezone.now()
        violations = []
        warnings = []
        
        # Verificar bloqueo temporal existente
        is_blocked, blocked_until = SecurityManager.is_user_blocked(user)
        if is_blocked:
            violations.append({
                'type': 'user_blocked',
                'message': f"Usuario bloqueado temporalmente hasta {blocked_until.strftime('%H:%M')}",
                'blocked_until': blocked_until
            })
            return False, violations, warnings
        
        # Obtener reservas del usuario
        from rooms.models import Reservation
        user_reservations = Reservation.objects.filter(user=user)
        
        # Verificar límite por hora
        hour_ago = now - timedelta(hours=1)
        recent_reservations = user_reservations.filter(
            created_at__gte=hour_ago,
            status__in=['confirmed', 'in_progress']
        ).count()
        
        if recent_reservations >= rules.max_reservations_per_hour:
            violations.append({
                'type': 'hourly_limit',
                'message': f"Límite por hora excedido ({recent_reservations}/{rules.max_reservations_per_hour})",
                'current': recent_reservations,
                'limit': rules.max_reservations_per_hour
            })
        elif recent_reservations >= rules.max_reservations_per_hour * rules.warning_threshold:
            warnings.append({
                'type': 'hourly_warning',
                'message': f"Cerca del límite por hora ({recent_reservations}/{rules.max_reservations_per_hour})",
                'current': recent_reservations,
                'limit': rules.max_reservations_per_hour
            })
        
        # Verificar límite por día
        day_ago = now - timedelta(days=1)
        daily_reservations = user_reservations.filter(
            created_at__gte=day_ago,
            status__in=['confirmed', 'in_progress']
        ).count()
        
        if daily_reservations >= rules.max_reservations_per_day:
            violations.append({
                'type': 'daily_limit',
                'message': f"Límite diario excedido ({daily_reservations}/{rules.max_reservations_per_day})",
                'current': daily_reservations,
                'limit': rules.max_reservations_per_day
            })
        elif daily_reservations >= rules.max_reservations_per_day * rules.warning_threshold:
            warnings.append({
                'type': 'daily_warning',
                'message': f"Cerca del límite diario ({daily_reservations}/{rules.max_reservations_per_day})",
                'current': daily_reservations,
                'limit': rules.max_reservations_per_day
            })
        
        # Verificar límite por semana
        week_ago = now - timedelta(days=7)
        weekly_reservations = user_reservations.filter(
            created_at__gte=week_ago,
            status__in=['confirmed', 'in_progress']
        ).count()
        
        if weekly_reservations >= rules.max_reservations_per_week:
            violations.append({
                'type': 'weekly_limit',
                'message': f"Límite semanal excedido ({weekly_reservations}/{rules.max_reservations_per_week})",
                'current': weekly_reservations,
                'limit': rules.max_reservations_per_week
            })
        
        # Verificar reservas concurrentes (activas ahora)
        concurrent_reservations = user_reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__lte=now,
            end_time__gt=now
        ).count()
        
        if concurrent_reservations >= rules.max_concurrent_reservations:
            violations.append({
                'type': 'concurrent_limit',
                'message': f"Límite de reservas simultáneas excedido ({concurrent_reservations}/{rules.max_concurrent_reservations})",
                'current': concurrent_reservations,
                'limit': rules.max_concurrent_reservations
            })
        
        # Si hay violaciones múltiples, considerar bloqueo temporal
        if len(violations) >= 2 and rules.enable_pattern_detection:
            SecurityManager.block_user_temporarily(
                user, 
                rules.block_duration_minutes,
                f"Múltiples violaciones de límites: {', '.join([v['type'] for v in violations])}"
            )
            return False, violations, warnings
        
        return len(violations) == 0, violations, warnings
    
    @staticmethod
    def check_duration_limits(user, start_time, end_time):
        """
        Verificar límites de duración total de reservas.
        
        Args:
            user: Usuario que hace la reserva
            start_time: Hora de inicio de la nueva reserva
            end_time: Hora de fin de la nueva reserva
            
        Returns:
            tuple: (is_allowed: bool, violations: list)
        """
        rules = SecurityManager.get_security_rules(user)
        violations = []
        
        # Calcular duración de la nueva reserva
        new_duration = (end_time - start_time).total_seconds() / 3600  # En horas
        
        from rooms.models import Reservation
        user_reservations = Reservation.objects.filter(user=user)
        
        # Verificar límite de horas por día
        start_date = start_time.date()
        daily_reservations = user_reservations.filter(
            start_time__date=start_date,
            status__in=['confirmed', 'in_progress']
        )
        
        daily_hours = sum([
            (res.end_time - res.start_time).total_seconds() / 3600
            for res in daily_reservations
        ])
        
        if daily_hours + new_duration > rules.max_total_hours_per_day:
            violations.append({
                'type': 'daily_hours_limit',
                'message': f"Límite de horas diarias excedido ({daily_hours + new_duration:.1f}/{rules.max_total_hours_per_day})",
                'current': daily_hours + new_duration,
                'limit': rules.max_total_hours_per_day
            })
        
        # Verificar límite de horas por semana
        week_start = start_time - timedelta(days=start_time.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        weekly_reservations = user_reservations.filter(
            start_time__gte=week_start,
            start_time__lt=week_start + timedelta(days=7),
            status__in=['confirmed', 'in_progress']
        )
        
        weekly_hours = sum([
            (res.end_time - res.start_time).total_seconds() / 3600
            for res in weekly_reservations
        ])
        
        if weekly_hours + new_duration > rules.max_total_hours_per_week:
            violations.append({
                'type': 'weekly_hours_limit',
                'message': f"Límite de horas semanales excedido ({weekly_hours + new_duration:.1f}/{rules.max_total_hours_per_week})",
                'current': weekly_hours + new_duration,
                'limit': rules.max_total_hours_per_week
            })
        
        return len(violations) == 0, violations
    
    @staticmethod
    def detect_suspicious_patterns(user):
        """
        Detectar patrones sospechosos de comportamiento.
        
        Analiza logs de uso para identificar comportamientos anómalos
        como intentos masivos, patrones de cancelación, etc.
        """
        suspicions = []
        now = timezone.now()
        
        # Analizar últimas 24 horas
        recent_logs = ReservationUsageLog.objects.filter(
            user=user,
            timestamp__gte=now - timedelta(hours=24)
        ).order_by('-timestamp')
        
        # Patrón 1: Muchos intentos bloqueados
        blocked_attempts = recent_logs.filter(action='attempt_blocked').count()
        if blocked_attempts >= 5:
            suspicions.append({
                'type': 'excessive_blocked_attempts',
                'message': f"Demasiados intentos bloqueados en 24h: {blocked_attempts}",
                'severity': 'high'
            })
        
        # Patrón 2: Creación y cancelación rápida
        quick_cancellations = 0
        for log in recent_logs.filter(action='create'):
            # Buscar cancelaciones de la misma reserva en menos de 5 minutos
            quick_cancel = recent_logs.filter(
                action='cancel',
                reservation_id=log.reservation_id,
                timestamp__gt=log.timestamp,
                timestamp__lt=log.timestamp + timedelta(minutes=5)
            ).exists()
            if quick_cancel:
                quick_cancellations += 1
        
        if quick_cancellations >= 3:
            suspicions.append({
                'type': 'quick_cancellation_pattern',
                'message': f"Patrón de cancelaciones rápidas: {quick_cancellations}",
                'severity': 'medium'
            })
        
        # Patrón 3: Reservas en múltiples IP/User-Agents
        unique_ips = set(log.ip_address for log in recent_logs if log.ip_address)
        if len(unique_ips) >= 5:
            suspicions.append({
                'type': 'multiple_ip_addresses',
                'message': f"Reservas desde múltiples IPs: {len(unique_ips)}",
                'severity': 'high'
            })
        
        return suspicions
    
    @staticmethod
    def log_action(user, action, room_name, reservation_id=None, ip_address=None, user_agent=None, additional_data=None):
        """Registrar una acción de reserva para análisis posterior."""
        try:
            ReservationUsageLog.objects.create(
                user=user,
                action=action,
                reservation_id=reservation_id,
                room_name=room_name,
                ip_address=ip_address,
                user_agent=user_agent,
                additional_data=additional_data or {}
            )
        except Exception as e:
            logger.error(f"Error registrando acción de seguridad: {e}")
    
    @staticmethod
    def validate_reservation_security(user, room, start_time, end_time, request=None):
        """
        Validación completa de seguridad para una nueva reserva.
        
        Esta es la función principal que debe llamarse antes de crear una reserva.
        
        Returns:
            dict: {
                'allowed': bool,
                'violations': list,
                'warnings': list,
                'suspicions': list
            }
        """
        # Obtener información de la request si está disponible
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Verificar límites de tasa
        rate_allowed, rate_violations, rate_warnings = SecurityManager.check_rate_limits(user)
        
        # Verificar límites de duración
        duration_allowed, duration_violations = SecurityManager.check_duration_limits(user, start_time, end_time)
        
        # Detectar patrones sospechosos
        suspicions = SecurityManager.detect_suspicious_patterns(user)
        
        # Combinar todas las violaciones
        all_violations = rate_violations + duration_violations
        
        # Determinar si la reserva está permitida
        is_allowed = rate_allowed and duration_allowed
        
        if not is_allowed:
            # Registrar intento bloqueado
            SecurityManager.log_action(
                user=user,
                action='attempt_blocked',
                room_name=room.name,
                ip_address=ip_address,
                user_agent=user_agent,
                additional_data={
                    'violations': [v['type'] for v in all_violations],
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
            )
        
        return {
            'allowed': is_allowed,
            'violations': all_violations,
            'warnings': rate_warnings,
            'suspicions': suspicions
        }


def initialize_default_security_rules():
    """Crear reglas de seguridad por defecto si no existen."""
    default_rules = [
        {
            'role': 'estudiante',
            'max_reservations_per_hour': 2,
            'max_reservations_per_day': 5,
            'max_reservations_per_week': 15,
            'max_total_hours_per_day': 6,
            'max_total_hours_per_week': 25,
            'max_concurrent_reservations': 2,
            'max_advance_days': 7,
            'block_duration_minutes': 30
        },
        {
            'role': 'profesor',
            'max_reservations_per_hour': 5,
            'max_reservations_per_day': 10,
            'max_reservations_per_week': 30,
            'max_total_hours_per_day': 10,
            'max_total_hours_per_week': 40,
            'max_concurrent_reservations': 5,
            'max_advance_days': 30,
            'block_duration_minutes': 60
        },
        {
            'role': 'admin',
            'max_reservations_per_hour': 20,
            'max_reservations_per_day': 50,
            'max_reservations_per_week': 100,
            'max_total_hours_per_day': 24,
            'max_total_hours_per_week': 100,
            'max_concurrent_reservations': 20,
            'max_advance_days': 365,
            'enable_pattern_detection': False,  # Admins exentos de detección de patrones
            'block_duration_minutes': 0
        },
        {
            'role': 'default',
            'max_reservations_per_hour': 1,
            'max_reservations_per_day': 3,
            'max_reservations_per_week': 10,
            'max_total_hours_per_day': 4,
            'max_total_hours_per_week': 15,
            'max_concurrent_reservations': 1,
            'max_advance_days': 7,
            'block_duration_minutes': 60
        }
    ]
    
    for rule_data in default_rules:
        rule, created = ReservationSecurityRule.objects.get_or_create(
            role=rule_data['role'],
            defaults=rule_data
        )
        if created:
            logger.info(f"Creada regla de seguridad por defecto para rol: {rule_data['role']}")
