from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import Room, Reservation
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea reservas de ejemplo para demostración del Colegio Clara Brincefield'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=30,
            help='Cantidad de reservas a crear (default: 30)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina reservas existentes antes de crear nuevas',
        )
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Período de días para crear reservas (default: 30)',
        )

    def handle(self, *args, **options):
        self.stdout.write("🏫 Creando reservas de ejemplo para Colegio Clara Brincefield...")
        
        if options['reset']:
            reservas_existentes = Reservation.objects.count()
            if reservas_existentes > 0:
                Reservation.objects.all().delete()
                self.stdout.write(f"🗑️ Eliminadas {reservas_existentes} reservas existentes")
        
        # Obtener usuarios y salas
        usuarios = list(User.objects.all())
        salas = list(Room.objects.filter(is_active=True))
        
        if not usuarios:
            self.stdout.write(self.style.ERROR("❌ No hay usuarios. Ejecuta: python manage.py setup_usuarios"))
            return
            
        if not salas:
            self.stdout.write(self.style.ERROR("❌ No hay salas. Ejecuta: python manage.py setup_colegio"))
            return
        
        cantidad = options['cantidad']
        dias_periodo = options['dias']
        reservas_creadas = 0
        intentos_fallidos = 0
        max_intentos = cantidad * 3  # Máximo 3 intentos por reserva deseada
        
        self.stdout.write(f"📅 Creando {cantidad} reservas en período de {dias_periodo} días...")
        
        # Crear reservas distribuidas respetando roles y permisos        # Crear reservas distribuidas respetando roles y permisos
        for intento in range(max_intentos):
            if reservas_creadas >= cantidad:
                break
                
            try:
                # Seleccionar usuario al azar
                usuario = random.choice(usuarios)
                
                # Obtener salas que este usuario puede reservar
                salas_disponibles = []
                for sala in salas:
                    if sala.can_be_reserved_by(usuario):
                        salas_disponibles.append(sala)
                
                if not salas_disponibles:
                    intentos_fallidos += 1
                    continue
                
                # Seleccionar sala de las disponibles para este usuario
                sala = random.choice(salas_disponibles)
                
                # Generar fecha y hora aleatoria
                dias_adelante = random.randint(0, dias_periodo)
                
                # Horarios según tipo de sala y usuario
                if sala.room_type in ['sala_individual', 'sala_estudio']:
                    # Salas de estudio: horarios más flexibles
                    hora_inicio = random.randint(8, 19)
                    duracion = random.choice([1, 2, 3, 4])
                elif sala.room_type == 'aula':
                    # Aulas: horarios de clase típicos
                    hora_inicio = random.choice([8, 10, 14, 16])
                    duracion = random.choice([2, 3])
                elif sala.room_type == 'laboratorio_informatica':
                    # Laboratorios: sesiones más largas
                    hora_inicio = random.choice([9, 11, 14, 16])
                    duracion = random.choice([2, 3, 4])
                elif sala.room_type == 'auditorio':
                    # Auditorios: eventos especiales
                    hora_inicio = random.choice([9, 14, 16])
                    duracion = random.choice([1, 2, 3])
                elif sala.room_type == 'equipamiento':
                    # Equipamiento: uso más corto
                    hora_inicio = random.randint(8, 16)
                    duracion = random.choice([1, 2])
                else:
                    # Otros tipos: horario estándar
                    hora_inicio = random.randint(8, 17)
                    duracion = random.choice([1, 2, 3])
                
                fecha_reserva = timezone.now().date() + timedelta(days=dias_adelante)
                hora_inicio_obj = timezone.now().replace(
                    year=fecha_reserva.year,
                    month=fecha_reserva.month,
                    day=fecha_reserva.day,
                    hour=hora_inicio,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                hora_fin_obj = hora_inicio_obj + timedelta(hours=duracion)
                
                # Verificar que esté dentro del horario de la sala
                if (hora_inicio_obj.time() < sala.opening_time or 
                    hora_fin_obj.time() > sala.closing_time):
                    intentos_fallidos += 1
                    continue
                
                # Verificar que no haya conflicto con otras reservas
                conflicto = Reservation.objects.filter(
                    room=sala,
                    start_time__lt=hora_fin_obj,
                    end_time__gt=hora_inicio_obj,
                    status__in=['confirmed', 'in_progress']
                ).exists()
                
                if not conflicto:
                    # Generar propósito según el tipo de sala y usuario
                    proposito = self.generar_proposito(sala, usuario)
                    
                    # Determinar número de asistentes
                    asistentes = self.calcular_asistentes(sala, usuario)
                    
                    # Crear la reserva
                    reserva = Reservation.objects.create(
                        user=usuario,
                        room=sala,
                        start_time=hora_inicio_obj,
                        end_time=hora_fin_obj,
                        purpose=proposito,
                        attendees_count=asistentes,
                        status='confirmed'
                    )
                    
                    reservas_creadas += 1
                    rol_display = usuario.get_role_display() if hasattr(usuario, 'role') else 'Usuario'
                    self.stdout.write(
                        f"   ✅ Reserva {reservas_creadas}: {usuario.get_full_name() or usuario.username} ({rol_display})"
                    )
                    self.stdout.write(f"      🏠 {sala.name}")
                    self.stdout.write(f"      📅 {fecha_reserva} de {hora_inicio}:00 a {hora_inicio + duracion}:00")
                    self.stdout.write(f"      📝 {proposito}")
                    self.stdout.write("")
                else:
                    intentos_fallidos += 1
                    
            except Exception as e:
                self.stdout.write(f"   ⚠️ Error creando reserva: {e}")
                intentos_fallidos += 1
                continue
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(f"✅ RESERVAS CREADAS: {reservas_creadas}")
        self.stdout.write(f"⚠️ Intentos fallidos: {intentos_fallidos}")
        self.stdout.write("="*70)
        
        # Mostrar estadísticas por rol
        self.stdout.write("\n📊 ESTADÍSTICAS POR ROL:")
        roles_stats = {}
        for usuario in usuarios:
            count = Reservation.objects.filter(user=usuario).count()
            if count > 0:
                rol = usuario.get_role_display() if hasattr(usuario, 'role') else 'Usuario'
                if rol not in roles_stats:
                    roles_stats[rol] = {'usuarios': 0, 'reservas': 0}
                roles_stats[rol]['usuarios'] += 1
                roles_stats[rol]['reservas'] += count
        
        for rol, stats in roles_stats.items():
            self.stdout.write(f"   {rol}: {stats['reservas']} reservas ({stats['usuarios']} usuarios)")
        
        # Mostrar estadísticas por tipo de sala
        self.stdout.write("\n📈 ESTADÍSTICAS POR TIPO DE SALA:")
        for room_type, room_name in Room.ROOM_TYPE_CHOICES:
            count = Reservation.objects.filter(room__room_type=room_type).count()
            if count > 0:
                self.stdout.write(f"   {room_name}: {count} reservas")
    
    def generar_proposito(self, sala, usuario):
        """Genera un propósito realista según el tipo de sala y usuario."""
        
        if hasattr(usuario, 'role'):
            rol = usuario.role
        else:
            rol = 'estudiante'
        
        if sala.room_type == 'aula':
            if rol == 'profesor':
                materias = ['Matemáticas', 'Historia', 'Ciencias Naturales', 'Literatura', 'Arte', 'Música', 'Educación Física']
                return f"Clase de {random.choice(materias)}"
            else:
                return f"Actividad educativa en {sala.name}"
                
        elif sala.room_type in ['sala_individual', 'sala_estudio']:
            actividades = [
                'Estudio personal de exámenes',
                'Preparación de proyecto final',
                'Investigación bibliográfica',
                'Trabajo individual concentrado',
                'Revisión de materias',
                'Preparación de presentación'
            ]
            return random.choice(actividades)
            
        elif sala.room_type == 'laboratorio_informatica':
            if rol == 'profesor':
                actividades = [
                    'Clase de Programación',
                    'Taller de Robótica',
                    'Curso de Informática',
                    'Práctica de Desarrollo Web',
                    'Clase de Diseño Digital'
                ]
            elif rol == 'soporte':
                actividades = [
                    'Mantenimiento de equipos',
                    'Instalación de software',
                    'Configuración de red',
                    'Capacitación técnica',
                    'Diagnóstico de sistemas'
                ]
            else:
                actividades = [
                    'Práctica de programación',
                    'Proyecto de robótica',
                    'Trabajo en computadoras'
                ]
            return random.choice(actividades)
            
        elif sala.room_type == 'auditorio':
            eventos = [
                'Conferencia educativa',
                'Presentación de proyectos',
                'Acto académico',
                'Reunión institucional',
                'Evento cultural',
                'Ceremonia escolar'
            ]
            return random.choice(eventos)
            
        elif sala.room_type == 'sala_reunion':
            if rol in ['profesor', 'admin']:
                reuniones = [
                    'Reunión de coordinación académica',
                    'Planificación curricular',
                    'Evaluación institucional',
                    'Reunión de profesores',
                    'Consejo académico'
                ]
            elif rol == 'soporte':
                reuniones = [
                    'Reunión del equipo técnico',
                    'Planificación de mantenimiento',
                    'Coordinación de soporte',
                    'Evaluación de sistemas'
                ]
            else:
                reuniones = ['Reunión estudiantil', 'Actividad grupal']
            return random.choice(reuniones)
            
        elif sala.room_type == 'equipamiento':
            if 'Proyector' in sala.name:
                return f"Uso de proyector para presentación"
            elif 'Laptop' in sala.name or 'Tablet' in sala.name:
                return f"Uso de dispositivos móviles para clase"
            elif 'Robótica' in sala.name:
                return f"Taller de robótica educativa"
            elif 'Sonido' in sala.name:
                return f"Evento con sistema de sonido"
            else:
                return f"Uso de {sala.name}"
                
        else:
            return f"Actividad en {sala.name}"
    
    def calcular_asistentes(self, sala, usuario):
        """Calcula un número realista de asistentes."""
        
        if sala.room_type in ['sala_individual']:
            return 1
        elif sala.room_type in ['sala_estudio']:
            return random.randint(1, min(6, sala.capacity))
        elif sala.room_type == 'aula':
            return random.randint(15, min(sala.capacity, 30))
        elif sala.room_type == 'laboratorio_informatica':
            return random.randint(10, min(sala.capacity, 25))
        elif sala.room_type == 'auditorio':
            return random.randint(20, min(sala.capacity, 100))
        elif sala.room_type == 'sala_reunion':
            return random.randint(3, min(sala.capacity, 12))
        elif sala.room_type == 'equipamiento':
            return 1
        else:
            return random.randint(1, min(sala.capacity, 10))
