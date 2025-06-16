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
        rooms_data = [
            # Aulas principales
            {
                'name': 'Aula 1A - Primaria',
                'description': 'Aula principal para estudiantes de primer grado. Equipada con mobiliario adaptado para niños y materiales didácticos básicos.',
                'capacity': 25,
                'equipment': 'Pizarra acrílica, proyector, computadora, sistema de sonido, estantes para libros, mobiliario infantil',
                'location': 'Edificio Principal - Primer Piso - Ala Este',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 2B - Primaria',
                'description': 'Aula para estudiantes de segundo grado con enfoque en matemáticas y ciencias básicas.',
                'capacity': 25,
                'equipment': 'Pizarra digital interactiva, proyector, tablets educativas, manipulativos matemáticos, cámara de documentos',
                'location': 'Edificio Principal - Primer Piso - Ala Oeste',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 6A - Primaria Superior',
                'description': 'Aula para estudiantes de sexto grado, preparación para secundaria.',
                'capacity': 30,
                'equipment': 'Pizarra inteligente, proyector HD, laptops, impresora, biblioteca de aula, microscopios básicos',
                'location': 'Edificio Principal - Segundo Piso - Ala Norte',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 7A - Secundaria',
                'description': 'Aula principal para estudiantes de séptimo grado, transición a educación secundaria.',
                'capacity': 32,
                'equipment': 'Sistema audiovisual completo, laptops, pizarra digital, conexión a internet de alta velocidad',
                'location': 'Edificio Secundaria - Primer Piso - Ala Central',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Aula 10B - Secundaria',
                'description': 'Aula para estudiantes de décimo grado con enfoque en preparación universitaria.',
                'capacity': 35,
                'equipment': 'Proyector 4K, sistema de conferencias, laptops individuales, impresora 3D básica, calculadoras científicas',
                'location': 'Edificio Secundaria - Segundo Piso - Ala Sur',
                'room_type': 'aula',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            
            # Laboratorios
            {
                'name': 'Laboratorio de Ciencias - Química',
                'description': 'Laboratorio especializado en química con equipamiento de seguridad completo y reactivos básicos.',
                'capacity': 24,
                'equipment': 'Mesas de laboratorio con agua y gas, campana extractora, microscopios ópticos, balanzas analíticas, material de vidrio, reactivos básicos, kit de primeros auxilios',
                'location': 'Edificio Ciencias - Primer Piso',
                'room_type': 'laboratorio_ciencias',
                'opening_time': '07:00',
                'closing_time': '17:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Laboratorio de Ciencias - Biología',
                'description': 'Laboratorio de biología con equipamiento para observación y experimentación.',
                'capacity': 28,
                'equipment': 'Microscopios binoculares, estereoscopios, modelos anatómicos, terrarios, acuarios, esqueletos didácticos, láminas histológicas',
                'location': 'Edificio Ciencias - Segundo Piso',
                'room_type': 'laboratorio_ciencias',
                'opening_time': '07:00',
                'closing_time': '17:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Laboratorio de Informática 1',
                'description': 'Laboratorio principal de computación con equipos de última generación.',
                'capacity': 30,
                'equipment': '30 computadoras de escritorio, servidor local, proyector, pizarra digital, impresora láser, escáner, kit de robótica básica',
                'location': 'Edificio Tecnología - Primer Piso',
                'room_type': 'laboratorio_informatica',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor,estudiante'
            },
            {
                'name': 'Laboratorio de Informática 2 - Robótica',
                'description': 'Laboratorio especializado en robótica y programación avanzada.',
                'capacity': 20,
                'equipment': 'Laptops de alto rendimiento, kits de robótica LEGO Mindstorms, Arduino, Raspberry Pi, impresora 3D profesional, soldadores, multímetros',
                'location': 'Edificio Tecnología - Segundo Piso',
                'room_type': 'laboratorio_informatica',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            
            # Espacios especiales
            {
                'name': 'Biblioteca Clara Brincefield',
                'description': 'Biblioteca principal del colegio con zona de estudio silencioso y recursos digitales.',
                'capacity': 50,
                'equipment': 'Catálogo digital, computadoras de consulta, impresora, scanner, proyector para presentaciones, zona de lectura cómoda',
                'location': 'Edificio Central - Primer Piso',
                'room_type': 'biblioteca',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,profesor,estudiante'
            },
            {
                'name': 'Auditorio Principal',
                'description': 'Auditorio para eventos, conferencias y presentaciones institucionales.',
                'capacity': 200,
                'equipment': 'Sistema de sonido profesional, proyectores de alta definición, iluminación escénica, micrófono inalámbrico, cámaras de video',
                'location': 'Edificio Central - Planta Baja',
                'room_type': 'auditorio',
                'opening_time': '07:00',
                'closing_time': '21:00',
                'allowed_roles': 'admin'
            },
            {
                'name': 'Sala de Profesores',
                'description': 'Espacio privado para reuniones del personal docente y planificación académica.',
                'capacity': 25,
                'equipment': 'Mesa de reuniones, proyector, laptops institucionales, impresora, cafetera, casilleros personales',
                'location': 'Edificio Administrativo - Segundo Piso',
                'room_type': 'sala_profesores',
                'opening_time': '06:30',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Sala de Reuniones - Dirección',
                'description': 'Sala de reuniones para la dirección académica y administrativa.',
                'capacity': 12,
                'equipment': 'Mesa ejecutiva, sistema de videoconferencias, proyector, laptops, teléfono de conferencias',
                'location': 'Edificio Administrativo - Segundo Piso',
                'room_type': 'sala_reunion',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin'
            },
            
            # Equipamiento móvil/recursos
            {
                'name': 'Carrito de Laptops - Set A',
                'description': 'Conjunto de 25 laptops educativas con carrito de carga para uso en cualquier aula.',
                'capacity': 1,
                'equipment': '25 laptops educativas, carrito con sistema de carga, router WiFi móvil, cables y accesorios',
                'location': 'Depósito de Tecnología - Edificio Principal',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Carrito de Tablets - Set B',
                'description': 'Conjunto de 30 tablets educativas para actividades interactivas.',
                'capacity': 1,
                'equipment': '30 tablets Android educativas, aplicaciones pedagógicas, carrito con carga inalámbrica, fundas protectoras',
                'location': 'Depósito de Tecnología - Edificio Principal',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Videoproyector Portátil - VP001',
                'description': 'Proyector de alta definición para presentaciones en cualquier espacio.',
                'capacity': 1,
                'equipment': 'Proyector HD, cables HDMI y VGA, control remoto, estuche de transporte, trípode',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Videoproyector Portátil - VP002',
                'description': 'Segundo proyector móvil de respaldo para eventos simultáneos.',
                'capacity': 1,
                'equipment': 'Proyector HD, cables múltiples, control remoto, estuche de transporte, trípode',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Kit de Microscopios - Ciencias',
                'description': 'Conjunto de microscopios portátiles para prácticas de laboratorio.',
                'capacity': 1,
                'equipment': '15 microscopios ópticos, láminas preparadas, porta y cubreobjetos, maletín de transporte',
                'location': 'Laboratorio de Biología - Almacén',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '17:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Kit de Robótica Educativa - LEGO',
                'description': 'Kits de robótica LEGO Mindstorms para clases de tecnología.',
                'capacity': 1,
                'equipment': '10 kits LEGO Mindstorms EV3, sensores adicionales, pistas de competencia, manual de actividades',
                'location': 'Laboratorio de Robótica - Almacén',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '19:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Cámara de Documentos - CD001',
                'description': 'Cámara para mostrar documentos y objetos en tiempo real.',
                'capacity': 1,
                'equipment': 'Cámara de documentos con zoom, conexión USB, software incluido, base articulada',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '18:00',
                'allowed_roles': 'admin,profesor'
            },
            {
                'name': 'Sistema de Sonido Portátil',
                'description': 'Equipo de sonido móvil para eventos al aire libre y presentaciones.',
                'capacity': 1,
                'equipment': 'Altavoces amplificados, micrófonos inalámbricos, mezcladora, cables, batería portátil',
                'location': 'Depósito Audiovisual - Edificio Central',
                'room_type': 'equipamiento',
                'opening_time': '07:00',
                'closing_time': '20:00',
                'allowed_roles': 'admin,profesor'
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
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 ¡Configuración completada para el Colegio Clara Brincefield!'
            )
        )
        self.stdout.write(f'📊 Total de salas/equipamiento creado: {created_count}')
        
        # Estadísticas por tipo
        stats = {}
        for room_type, room_name in Room.ROOM_TYPE_CHOICES:
            count = Room.objects.filter(room_type=room_type).count()
            if count > 0:
                stats[room_name] = count
        
        self.stdout.write('\n📈 Distribución por tipo:')
        for tipo, cantidad in stats.items():
            self.stdout.write(f'   • {tipo}: {cantidad}')
        
        self.stdout.write('\n🏫 El sistema está listo para ser usado en el Colegio Clara Brincefield')
        self.stdout.write('💡 Recuerda que el campo "valor" está oculto en los formularios pero se mantiene en el modelo')
        self.stdout.write('🔧 Todos los recursos están configurados como gratuitos (valor = 0.00)')
