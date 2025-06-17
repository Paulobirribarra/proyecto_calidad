"""
Comando de gestión para configurar el Colegio Clara Brincefield.

Este comando elimina todas las salas existentes y crea nuevas salas
y equipamiento apropiado para un colegio.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import Room
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Configura salas y equipamiento para el Colegio Clara Brincefield'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Eliminar todas las salas existentes antes de crear las nuevas',
        )
    
    def handle(self, *args, **options):
        """Ejecutar el comando para configurar el colegio."""
        
        self.stdout.write(
            self.style.SUCCESS('🏫 Configurando Colegio Clara Brincefield...')
        )
        
        # Eliminar salas existentes si se especifica
        if options['delete_existing']:
            deleted_count = Room.objects.all().count()
            Room.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'✅ Eliminadas {deleted_count} salas existentes')
            )
        
        # Obtener usuario admin para asignar como creador
        admin_user = None
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
        except:
            pass
          # Datos de salas y equipamiento para el colegio
        # Organizados por roles para asegurar distribución equilibrada
        rooms_data = [
            # SALAS PARA ESTUDIANTES (6+ salas)
            # Salas de estudio individuales
            {
                'name': 'Sala de Estudio Individual A1',
                'description': 'Sala de estudio individual equipada para concentración y trabajo personal.',
                'capacity': 1,
                'equipment': 'Escritorio, silla ergonómica, lámpara de lectura, conexión eléctrica, WiFi',
                'location': 'Edificio Biblioteca - Primer Piso',
                'room_type': 'sala_individual',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,estudiante'
            },
            {
                'name': 'Sala de Estudio Individual A2',
                'description': 'Cabina de estudio con ambiente silencioso para concentración máxima.',
                'capacity': 1,
                'equipment': 'Escritorio amplio, silla cómoda, lámpara LED, toma corriente, ambiente silencioso',
                'location': 'Edificio Biblioteca - Primer Piso',
                'room_type': 'sala_individual',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,estudiante'
            },
            {
                'name': 'Sala de Estudio Individual A3',
                'description': 'Espacio personal de estudio con vista al jardín para un ambiente relajante.',
                'capacity': 1,
                'equipment': 'Mesa de estudio, silla ajustable, luz natural, conexión a internet',
                'location': 'Edificio Biblioteca - Segundo Piso',
                'room_type': 'sala_individual',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,estudiante'
            },
            
            # Salas de estudio grupales para estudiantes
            {
                'name': 'Sala de Estudio Grupal B1',
                'description': 'Sala para grupos de estudio de 4-6 estudiantes con pizarra.',
                'capacity': 6,
                'equipment': 'Mesa redonda, 6 sillas, pizarra acrílica, marcadores, proyector portátil',
                'location': 'Edificio Biblioteca - Primer Piso',
                'room_type': 'sala_estudio',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,estudiante'
            },
            {
                'name': 'Sala de Estudio Grupal B2',
                'description': 'Espacio colaborativo para proyectos grupales y discusión.',
                'capacity': 8,
                'equipment': 'Mesas modulares, 8 sillas, pizarra interactiva, TV, conexión HDMI',
                'location': 'Edificio Biblioteca - Segundo Piso',
                'room_type': 'sala_estudio',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,estudiante'
            },
            {
                'name': 'Sala de Estudio Grupal B3',
                'description': 'Sala multiuso para trabajo en equipo y presentaciones estudiantiles.',
                'capacity': 10,
                'equipment': 'Mesa de conferencias, 10 sillas, proyector, pantalla, laptop compartida',
                'location': 'Edificio Estudiantes - Primer Piso',
                'room_type': 'sala_estudio',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,estudiante'
            },
            {
                'name': 'Auditorio Estudiantil',
                'description': 'Pequeño auditorio para presentaciones y actividades estudiantiles.',
                'capacity': 50,
                'equipment': 'Asientos tipo anfiteatro, proyector, sistema de sonido, micrófono',
                'location': 'Edificio Estudiantes - Planta Baja',
                'room_type': 'auditorio',
                'opening_time': '08:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,estudiante'
            },
            
            # SALAS PARA PROFESORES (6+ salas)
            # Aulas de clases
            {
                'name': 'Aula 1A - Primaria',
                'description': 'Aula principal para estudiantes de primer grado con mobiliario adaptado.',
                'capacity': 25,
                'equipment': 'Pizarra acrílica, proyector, computadora, sistema de sonido, mobiliario infantil',
                'location': 'Edificio Principal - Primer Piso',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 2B - Primaria',
                'description': 'Aula para segundo grado con tecnología educativa integrada.',
                'capacity': 25,
                'equipment': 'Pizarra digital interactiva, tablets educativas, manipulativos matemáticos',
                'location': 'Edificio Principal - Primer Piso',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 6A - Primaria Superior',
                'description': 'Aula para sexto grado con preparación para secundaria.',
                'capacity': 30,
                'equipment': 'Pizarra inteligente, laptops, impresora, biblioteca de aula, microscopios',
                'location': 'Edificio Principal - Segundo Piso',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 7A - Secundaria',
                'description': 'Aula principal para séptimo grado con tecnología avanzada.',
                'capacity': 32,
                'equipment': 'Sistema audiovisual completo, laptops, pizarra digital, internet alta velocidad',
                'location': 'Edificio Secundaria - Primer Piso',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 10B - Secundaria',
                'description': 'Aula para décimo grado con preparación universitaria.',
                'capacity': 35,
                'equipment': 'Proyector 4K, sistema conferencias, laptops individuales, impresora 3D',
                'location': 'Edificio Secundaria - Segundo Piso',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula de Arte y Creatividad',
                'description': 'Espacio especializado para clases de arte, música y actividades creativas.',
                'capacity': 20,
                'equipment': 'Mesas de arte, caballetes, proyector, equipo de sonido, materiales básicos',
                'location': 'Edificio Cultural - Primer Piso',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            
            # Auditorio principal
            {
                'name': 'Auditorio Principal Clara Brincefield',
                'description': 'Auditorio principal para eventos, conferencias y presentaciones institucionales.',
                'capacity': 200,
                'equipment': 'Sistema sonido profesional, proyectores HD, iluminación escénica, cámaras',
                'location': 'Edificio Central - Planta Baja',
                'room_type': 'auditorio',
                'opening_time': '07:00',
                'closing_time': '21:00',
                'allowed_roles': 'admin,profesor'
            },
            
            # Salas de reuniones para profesores
            {
                'name': 'Sala de Profesores Principal',
                'description': 'Espacio principal para reuniones del personal docente y planificación.',
                'capacity': 25,
                'equipment': 'Mesa reuniones, proyector, laptops, impresora, cafetera, casilleros',
                'location': 'Edificio Administrativo - Segundo Piso',
                'room_type': 'sala_reunion',
                'opening_time': '06:30',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Sala de Coordinación Académica',
                'description': 'Sala para coordinadores académicos y reuniones de área.',
                'capacity': 12,
                'equipment': 'Mesa ejecutiva, sistema videoconferencias, proyector, teléfono conferencias',
                'location': 'Edificio Administrativo - Primer Piso',
                'room_type': 'sala_reunion',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            
            # SALAS PARA SOPORTE TÉCNICO (6+ salas/equipos)
            # Laboratorios de informática
            {
                'name': 'Laboratorio de Informática 1',
                'description': 'Laboratorio principal de computación con equipos de última generación.',
                'capacity': 30,
                'equipment': '30 computadoras, servidor local, proyector, pizarra digital, impresora láser',
                'location': 'Edificio Tecnología - Primer Piso',
                'room_type': 'laboratorio_informatica',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Laboratorio de Informática 2 - Robótica',
                'description': 'Laboratorio especializado en robótica y programación avanzada.',
                'capacity': 20,
                'equipment': 'Laptops alto rendimiento, kits robótica, Arduino, impresora 3D profesional',
                'location': 'Edificio Tecnología - Segundo Piso',
                'room_type': 'laboratorio_informatica',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Laboratorio de Reparación Técnica',
                'description': 'Espacio para mantenimiento y reparación de equipos tecnológicos.',
                'capacity': 5,
                'equipment': 'Banco trabajo, herramientas especializadas, multímetros, soldadores, repuestos',
                'location': 'Edificio Tecnología - Sótano',
                'room_type': 'laboratorio_informatica',
                'opening_time': '08:00',
                'closing_time': '17:00',
                'allowed_roles': 'admin,soporte'
            },
            
            # Salas de reuniones para soporte
            {
                'name': 'Sala de Reuniones Técnicas',
                'description': 'Sala para reuniones del equipo de soporte técnico y planificación IT.',
                'capacity': 8,
                'equipment': 'Mesa reuniones, laptops, proyector, pizarra, conexión múltiples dispositivos',
                'location': 'Edificio Tecnología - Primer Piso',
                'room_type': 'sala_reunion',
                'opening_time': '08:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,soporte'
            },
            {
                'name': 'Centro de Soporte Técnico',
                'description': 'Centro principal de atención y soporte técnico para usuarios.',
                'capacity': 6,
                'equipment': 'Escritorios de atención, computadoras, teléfonos, sistema tickets, almacén',
                'location': 'Edificio Tecnología - Planta Baja',
                'room_type': 'sala_reunion',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,soporte'
            },
            
            # Auditorio para soporte (capacitaciones técnicas)
            {
                'name': 'Aula de Capacitación Técnica',
                'description': 'Espacio para capacitaciones técnicas y entrenamientos del personal.',
                'capacity': 30,
                'equipment': 'Proyector, sistema sonido, laptops, simuladores, material didáctico técnico',
                'location': 'Edificio Tecnología - Segundo Piso',
                'room_type': 'auditorio',
                'opening_time': '08:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,soporte'
            },
            
            # EQUIPAMIENTO MÓVIL (Accesible para múltiples roles)
            {
                'name': 'Videoproyector Portátil - VP001',
                'description': 'Proyector de alta definición para presentaciones móviles.',
                'capacity': 1,
                'equipment': 'Proyector HD, cables HDMI/VGA, control remoto, estuche, trípode',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Videoproyector Portátil - VP002',
                'description': 'Segundo proyector móvil para eventos simultáneos.',
                'capacity': 1,
                'equipment': 'Proyector HD, cables múltiples, control remoto, estuche, trípode',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Carrito de Laptops - Set A',
                'description': 'Conjunto de 25 laptops educativas con carrito de carga móvil.',
                'capacity': 1,
                'equipment': '25 laptops educativas, carrito carga, router WiFi móvil, cables',
                'location': 'Depósito Tecnología - Edificio Principal',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Carrito de Tablets - Set B',
                'description': 'Conjunto de 30 tablets educativas para actividades interactivas.',
                'capacity': 1,
                'equipment': '30 tablets Android educativas, apps pedagógicas, carga inalámbrica',
                'location': 'Depósito Tecnología - Edificio Principal',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Kit de Robótica Educativa - LEGO',
                'description': 'Kits de robótica LEGO Mindstorms para clases de tecnología.',
                'capacity': 1,
                'equipment': '10 kits LEGO Mindstorms EV3, sensores, pistas competencia, manuales',
                'location': 'Laboratorio Robótica - Almacén',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Sistema de Sonido Portátil',
                'description': 'Equipo de sonido móvil para eventos y presentaciones.',
                'capacity': 1,
                'equipment': 'Altavoces amplificados, micrófonos inalámbricos, mezcladora, batería',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Cámara de Documentos - CD001',
                'description': 'Cámara para mostrar documentos y objetos en tiempo real.',
                'capacity': 1,
                'equipment': 'Cámara documentos con zoom, conexión USB, software, base articulada',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            {
                'name': 'Impresora 3D Educativa',
                'description': 'Impresora 3D para proyectos educativos y prototipos.',
                'capacity': 1,
                'equipment': 'Impresora 3D, filamentos PLA, software diseño 3D, herramientas',
                'location': 'Laboratorio Tecnología - Almacén',
                'room_type': 'equipamiento',
                'opening_time': '08:00',
                'closing_time': '17:00',
                'allowed_roles': 'admin,profesor,soporte'
            },
            
            # ESPACIOS ADICIONALES PARA ADMIN (acceso total)
            {
                'name': 'Biblioteca Clara Brincefield',
                'description': 'Biblioteca principal del colegio con recursos digitales y físicos.',
                'capacity': 50,
                'equipment': 'Catálogo digital, computadoras consulta, impresora, scanner, zona lectura',
                'location': 'Edificio Central - Primer Piso',
                'room_type': 'biblioteca',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,profesor,estudiante,soporte'
            },
            {
                'name': 'Sala de Dirección Ejecutiva',
                'description': 'Sala de reuniones para la dirección y junta directiva.',
                'capacity': 15,
                'equipment': 'Mesa ejecutiva, sistema videoconferencias 4K, proyector, teléfono conferencias',
                'location': 'Edificio Administrativo - Tercer Piso',
                'room_type': 'sala_reunion',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin'
            },
            {
                'name': 'Sala de Servidores',
                'description': 'Centro de datos principal del colegio con servidores y sistemas críticos.',
                'capacity': 2,
                'equipment': 'Servidores principales, sistema de respaldo, UPS, control ambiental',
                'location': 'Edificio Tecnología - Sótano',
                'room_type': 'sala_servidor',
                'opening_time': '00:00',
                'closing_time': '23:59',
                'allowed_roles': 'admin'
            }
        ]
        
        # Crear salas y equipamiento
        created_count = 0
        for room_data in rooms_data:
            # Convertir horarios string a objetos time
            from datetime import time
            
            opening_time = time(*map(int, room_data['opening_time'].split(':')))
            closing_time = time(*map(int, room_data['closing_time'].split(':')))
            
            room = Room.objects.create(
                name=room_data['name'],
                description=room_data['description'],
                capacity=room_data['capacity'],
                equipment=room_data['equipment'],
                location=room_data['location'],
                room_type=room_data['room_type'],
                opening_time=opening_time,
                closing_time=closing_time,
                allowed_roles=room_data['allowed_roles'],
                hourly_rate=0.00,  # Gratis para el colegio
                is_active=True,
                created_by=admin_user
            )
            
            created_count += 1
            self.stdout.write(f'✅ Creado: {room.name}')
          # Resumen final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 ¡Configuración completada para el Colegio Clara Brincefield!'
            )
        )
        self.stdout.write(f'📊 Total de salas/equipamiento creado: {created_count}')
        
        # Estadísticas por tipo de sala
        stats = {}
        for room_type, room_name in Room.ROOM_TYPE_CHOICES:
            count = Room.objects.filter(room_type=room_type).count()
            if count > 0:
                stats[room_name] = count
        
        self.stdout.write('\n📈 Distribución por tipo de sala:')
        for tipo, cantidad in stats.items():
            self.stdout.write(f'   • {tipo}: {cantidad}')
        
        # Estadísticas por roles - contando salas accesibles
        self.stdout.write('\n� Salas accesibles por rol:')
        
        roles_stats = {
            'estudiante': Room.objects.filter(allowed_roles__icontains='estudiante').count(),
            'profesor': Room.objects.filter(allowed_roles__icontains='profesor').count(),
            'soporte': Room.objects.filter(allowed_roles__icontains='soporte').count(),
            'admin': Room.objects.filter(allowed_roles__icontains='admin').count(),
        }
        
        role_names = {
            'estudiante': 'Estudiantes',
            'profesor': 'Profesores', 
            'soporte': 'Soporte Técnico',
            'admin': 'Administradores'
        }
        
        for role, count in roles_stats.items():
            name = role_names.get(role, role.title())
            self.stdout.write(f'   • {name}: {count} salas/equipos')
        
        # Detalles específicos por rol
        self.stdout.write('\n🔍 Detalles por rol:')
        
        # Estudiantes
        estudiante_rooms = Room.objects.filter(allowed_roles__icontains='estudiante')
        self.stdout.write(f'\n   👥 ESTUDIANTES ({estudiante_rooms.count()} salas):')
        for room_type in ['sala_individual', 'sala_estudio', 'auditorio', 'biblioteca']:
            count = estudiante_rooms.filter(room_type=room_type).count()
            type_name = dict(Room.ROOM_TYPE_CHOICES).get(room_type, room_type)
            if count > 0:
                self.stdout.write(f'      - {type_name}: {count}')
        
        # Profesores
        profesor_rooms = Room.objects.filter(allowed_roles__icontains='profesor')
        self.stdout.write(f'\n   �‍🏫 PROFESORES ({profesor_rooms.count()} salas):')
        for room_type in ['aula', 'auditorio', 'sala_reunion', 'equipamiento']:
            count = profesor_rooms.filter(room_type=room_type).count()
            type_name = dict(Room.ROOM_TYPE_CHOICES).get(room_type, room_type)
            if count > 0:
                self.stdout.write(f'      - {type_name}: {count}')
        
        # Soporte Técnico
        soporte_rooms = Room.objects.filter(allowed_roles__icontains='soporte')
        self.stdout.write(f'\n   🔧 SOPORTE TÉCNICO ({soporte_rooms.count()} salas):')
        for room_type in ['laboratorio_informatica', 'sala_reunion', 'auditorio', 'equipamiento']:
            count = soporte_rooms.filter(room_type=room_type).count()
            type_name = dict(Room.ROOM_TYPE_CHOICES).get(room_type, room_type)
            if count > 0:
                self.stdout.write(f'      - {type_name}: {count}')
        
        # Administradores
        admin_rooms = Room.objects.filter(allowed_roles__icontains='admin')
        self.stdout.write(f'\n   👑 ADMINISTRADORES ({admin_rooms.count()} salas):')
        self.stdout.write('      - Acceso total a todas las salas y equipamiento')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('🏫 El sistema está listo para demostración del Colegio Clara Brincefield')
        self.stdout.write('✅ Cada rol tiene al menos 6 salas/equipos disponibles')
        self.stdout.write('🔧 Todos los recursos están configurados como gratuitos (valor = 0.00)')
        self.stdout.write('📅 Los filtros del calendario mostrarán solo opciones relevantes por rol')
