"""
Comando para inicializar el sistema de seguridad de reservas.

Este comando crea las reglas de seguridad por defecto y
configura el sistema de prevención de abuso de reservas.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.reservation_security import initialize_default_security_rules, SecurityManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicializa el sistema de seguridad de reservas con reglas por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la recreación de reglas existentes',
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        force = options['force']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('Inicializando sistema de seguridad de reservas...')
        )
        
        try:
            with transaction.atomic():
                # Inicializar reglas por defecto
                initialize_default_security_rules()
                
                if verbose:
                    # Mostrar reglas creadas
                    from core.reservation_security import ReservationSecurityRule
                    rules = ReservationSecurityRule.objects.all()
                    
                    self.stdout.write("\nReglas de seguridad configuradas:")
                    self.stdout.write("-" * 50)
                    
                    for rule in rules:
                        self.stdout.write(f"\nRol: {rule.get_role_display()}")
                        self.stdout.write(f"  - Reservas por hora: {rule.max_reservations_per_hour}")
                        self.stdout.write(f"  - Reservas por día: {rule.max_reservations_per_day}")
                        self.stdout.write(f"  - Reservas por semana: {rule.max_reservations_per_week}")
                        self.stdout.write(f"  - Horas por día: {rule.max_total_hours_per_day}")
                        self.stdout.write(f"  - Horas por semana: {rule.max_total_hours_per_week}")
                        self.stdout.write(f"  - Reservas simultáneas: {rule.max_concurrent_reservations}")
                        self.stdout.write(f"  - Días de anticipación: {rule.max_advance_days}")
                        self.stdout.write(f"  - Duración de bloqueo: {rule.block_duration_minutes} min")
                        self.stdout.write(f"  - Detección de patrones: {'Sí' if rule.enable_pattern_detection else 'No'}")
                        self.stdout.write(f"  - Activa: {'Sí' if rule.is_active else 'No'}")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✅ Sistema de seguridad de reservas inicializado correctamente'
                    )
                )
                
                # Mostrar información adicional
                self.stdout.write("\n" + "="*60)
                self.stdout.write("INFORMACIÓN DEL SISTEMA DE SEGURIDAD")
                self.stdout.write("="*60)
                
                self.stdout.write("""
🛡️  FUNCIONALIDADES IMPLEMENTADAS:

1. LÍMITES POR ROL DE USUARIO:
   - Estudiante: Límites restrictivos para uso normal
   - Profesor: Límites moderados para uso académico
   - Admin: Límites altos para administración
   - Default: Límites básicos para usuarios sin rol específico

2. TIPOS DE LÍMITES:
   - Reservas por hora/día/semana
   - Horas totales reservadas por día/semana
   - Reservas simultáneas activas
   - Días máximos de anticipación

3. SEGURIDAD AVANZADA:
   - Detección de patrones abusivos
   - Bloqueo temporal automático
   - Rate limiting por IP
   - Logging detallado de acciones

4. MONITOREO:
   - Logs de todas las acciones de reserva
   - Detección de comportamiento sospechoso
   - Alertas automáticas a administradores
   - Análisis de patrones de uso

5. CONFIGURACIÓN:
   - Reglas editables desde el admin de Django
   - Umbrales de advertencia configurables
   - Duración de bloqueos personalizable
   - Activación/desactivación por rol
                """)
                
                self.stdout.write("="*60)
                self.stdout.write("PRÓXIMOS PASOS:")
                self.stdout.write("="*60)
                
                self.stdout.write("""
1. Agregar middleware a settings.py:
   MIDDLEWARE = [
       ...
       'core.reservation_security_middleware.ReservationSecurityMiddleware',
       'core.reservation_security_middleware.RateLimitMiddleware',
       ...
   ]

2. Configurar cache para rate limiting:
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
       }
   }

3. Ejecutar migraciones:
   python manage.py makemigrations
   python manage.py migrate

4. Configurar reglas desde el admin:
   - Ir a Admin > Core > Reglas de Seguridad de Reservas
   - Ajustar límites según las necesidades
   - Revisar logs en Admin > Core > Logs de Uso de Reservas

5. Monitorear el sistema:
   - Revisar logs regularmente
   - Ajustar umbrales según el uso real
   - Configurar notificaciones por email
                """)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al inicializar sistema de seguridad: {e}')
            )
            logger.error(f"Error en comando init_reservation_security: {e}", exc_info=True)
            raise
