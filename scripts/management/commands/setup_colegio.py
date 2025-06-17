from django.core.management.base import BaseCommand
from rooms.models import Room

class Command(BaseCommand):
    help = 'Elimina todas las salas existentes y crea salas específicas para el Colegio Clara Brincefield'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma que deseas eliminar todas las salas existentes',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'ADVERTENCIA: Este comando eliminará TODAS las salas existentes.\n'
                    'Para confirmar, ejecuta: python manage.py setup_colegio --confirm'
                )
            )
            return

        self.stdout.write("🏫 Configurando salas para Colegio Clara Brincefield...")
        
        # Eliminar salas existentes
        existing_count = Room.objects.count()
        Room.objects.all().delete()
        self.stdout.write(f"🗑️ Eliminadas {existing_count} salas existentes")
        
        # Definir salas y equipos del colegio
        items_colegio = [
            # AULAS
            {
                'name': 'Aula 1° Básico A',
                'description': 'Aula para estudiantes de primer año básico, equipada con pizarra interactiva y materiales didácticos.',
                'capacity': 30,
                'equipment': 'Pizarra interactiva, proyector, computador, sistema de audio, mobiliario adaptado para niños',
                'location': 'Edificio Principal - Piso 1',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Aula 2° Básico A',
                'description': 'Aula para estudiantes de segundo año básico con ambiente de aprendizaje estimulante.',
                'capacity': 28,
                'equipment': 'Pizarra tradicional, proyector, rincón de lectura, materiales manipulativos',
                'location': 'Edificio Principal - Piso 1',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Aula 6° Básico A',
                'description': 'Aula para estudiantes de sexto básico, preparándolos para la educación media.',
                'capacity': 35,
                'equipment': 'Pizarra interactiva, computadores, proyector, sistema de sonido',
                'location': 'Edificio Principal - Piso 2',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Aula 1° Medio A',
                'description': 'Aula para estudiantes de primer año medio con tecnología avanzada.',
                'capacity': 40,
                'equipment': 'Pizarra digital, tablets, proyector 4K, sistema audio surround',
                'location': 'Edificio Secundaria - Piso 1',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Aula 4° Medio A',
                'description': 'Aula para estudiantes de cuarto medio, enfocada en preparación universitaria.',
                'capacity': 38,
                'equipment': 'Pizarra interactiva, computadores portátiles, proyector, acceso a internet de alta velocidad',
                'location': 'Edificio Secundaria - Piso 2',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            
            # LABORATORIOS
            {
                'name': 'Laboratorio de Ciencias',
                'description': 'Laboratorio completamente equipado para experimentos de física, química y biología.',
                'capacity': 24,
                'equipment': 'Mesas de laboratorio, microscopios, instrumentos de medición, campana extractora, ducha de emergencia',
                'location': 'Edificio Ciencias - Piso 1',
                'room_type': 'laboratorio',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Laboratorio de Computación',
                'description': 'Sala con computadores modernos para enseñanza de informática y programación.',
                'capacity': 30,
                'equipment': '30 computadores de última generación, proyector, pizarra digital, impresora 3D',
                'location': 'Edificio Tecnología - Piso 1',
                'room_type': 'laboratorio',
                'allowed_roles': 'profesor,administrador'
            },
            
            # SALAS ESPECIALES
            {
                'name': 'Sala de Música',
                'description': 'Sala acondicionada acústicamente para clases de música y coro.',
                'capacity': 25,
                'equipment': 'Piano, instrumentos musicales, sistema de sonido profesional, aislamiento acústico',
                'location': 'Edificio Artes - Piso 1',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Sala de Arte',
                'description': 'Taller de arte con excelente iluminación natural y materiales especializados.',
                'capacity': 20,
                'equipment': 'Caballetes, mesas de trabajo, lavaderos, almacenamiento de materiales, ventilación especial',
                'location': 'Edificio Artes - Piso 2',
                'room_type': 'aula',
                'allowed_roles': 'profesor,administrador'
            },
            
            # ESPACIOS DE ESTUDIO
            {
                'name': 'Biblioteca - Sala Silenciosa',
                'description': 'Espacio de estudio individual en completo silencio.',
                'capacity': 15,
                'equipment': 'Escritorios individuales, iluminación LED, enchufes para dispositivos, wifi',
                'location': 'Biblioteca - Piso 1',
                'room_type': 'sala_individual',
                'allowed_roles': 'estudiante,profesor,administrador'
            },
            {
                'name': 'Biblioteca - Sala Grupal',
                'description': 'Espacio para trabajo en equipo y discusión grupal.',
                'capacity': 8,
                'equipment': 'Mesa grande, pizarra blanca, proyector portátil, sillas cómodas',
                'location': 'Biblioteca - Piso 1',
                'room_type': 'sala_estudio',
                'allowed_roles': 'estudiante,profesor,administrador'
            },
            
            # ESPACIOS ADMINISTRATIVOS
            {
                'name': 'Sala de Profesores',
                'description': 'Sala de reuniones para el cuerpo docente.',
                'capacity': 20,
                'equipment': 'Mesa de conferencias, proyector, sistema de videoconferencia, cafetera',
                'location': 'Edificio Administrativo - Piso 1',
                'room_type': 'sala_reunion',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Auditorio Clara Brincefield',
                'description': 'Auditorio principal para eventos, ceremonias y presentaciones importantes.',
                'capacity': 200,
                'equipment': 'Sistema de sonido profesional, iluminación escénica, proyector de gran formato, escenario',
                'location': 'Edificio Principal - Planta Baja',
                'room_type': 'auditorio',
                'allowed_roles': 'administrador'
            },
            
            # EQUIPOS TECNOLÓGICOS (como "salas" reservables)
            {
                'name': 'Videoproyector Portátil #001',
                'description': 'Videoproyector portátil de alta definición para presentaciones en cualquier aula.',
                'capacity': 1,
                'equipment': 'Proyector HD, cables HDMI/VGA, control remoto, maletín de transporte',
                'location': 'Centro de Recursos Tecnológicos',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Videoproyector Portátil #002',
                'description': 'Videoproyector portátil de alta definición para presentaciones en cualquier aula.',
                'capacity': 1,
                'equipment': 'Proyector HD, cables HDMI/VGA, control remoto, maletín de transporte',
                'location': 'Centro de Recursos Tecnológicos',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Set de Microscopios (10 unidades)',
                'description': 'Conjunto de 10 microscopios ópticos para clases de biología.',
                'capacity': 10,
                'equipment': '10 microscopios ópticos, láminas preparadas, aceite de inmersión, paños de limpieza',
                'location': 'Laboratorio de Ciencias',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Laptops Educativos (15 unidades)',
                'description': 'Set de 15 laptops para actividades educativas móviles.',
                'capacity': 15,
                'equipment': '15 laptops, cargadores, software educativo instalado, carrito de transporte',
                'location': 'Centro de Recursos Tecnológicos',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Tablets Educativas (20 unidades)',
                'description': 'Conjunto de tablets para actividades interactivas y aprendizaje digital.',
                'capacity': 20,
                'equipment': '20 tablets Android, apps educativas, fundas protectoras, estación de carga',
                'location': 'Centro de Recursos Tecnológicos',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Kit de Robótica Educativa',
                'description': 'Set completo de robótica para clases de STEM y programación.',
                'capacity': 8,
                'equipment': '8 kits de robótica, software de programación, sensores, motores, instructivos',
                'location': 'Laboratorio de Computación',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Cámara Fotográfica Profesional',
                'description': 'Cámara profesional para proyectos audiovisuales y documentación.',
                'capacity': 1,
                'equipment': 'Cámara DSLR, lentes intercambiables, trípode, tarjetas de memoria, baterías extra',
                'location': 'Centro de Recursos Tecnológicos',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            },
            {
                'name': 'Sistema de Audio Portátil',
                'description': 'Sistema de sonido móvil para eventos y presentaciones.',
                'capacity': 1,
                'equipment': 'Altavoces, micrófonos inalámbricos, mezcladora, cables, batería recargable',
                'location': 'Centro de Recursos Tecnológicos',
                'room_type': 'sala_individual',
                'allowed_roles': 'profesor,administrador'
            }
        ]
        
        created_count = 0
        
        for item_data in items_colegio:
            try:
                # Establecer valores por defecto para campos del colegio
                item_data['hourly_rate'] = 0.00  # Sin costo para el colegio
                item_data['is_active'] = True
                
                sala = Room.objects.create(**item_data)
                created_count += 1
                
                # Determinar emoji según el tipo
                if 'Videoproyector' in sala.name:
                    emoji = '📽️'
                elif 'Microscopio' in sala.name:
                    emoji = '🔬'
                elif 'Laptop' in sala.name or 'Tablet' in sala.name:
                    emoji = '💻'
                elif 'Robótica' in sala.name:
                    emoji = '🤖'
                elif 'Cámara' in sala.name:
                    emoji = '📷'
                elif 'Audio' in sala.name:
                    emoji = '🔊'
                elif sala.room_type == 'laboratorio':
                    emoji = '🧪'
                elif sala.room_type == 'auditorio':
                    emoji = '🎭'
                else:
                    emoji = '🏫'
                
                self.stdout.write(f"{emoji} Creado: {sala.name}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error con {item_data['name']}: {str(e)}")
                )
        
        self.stdout.write(f"\n📊 Resumen:")
        self.stdout.write(f"   - Salas/Equipos creados: {created_count}")
        self.stdout.write(f"   - Total items: {Room.objects.count()}")
        self.stdout.write(f"\n🎉 ¡Configuración del Colegio Clara Brincefield completada!")
        self.stdout.write(
            self.style.SUCCESS(
                "\n✨ El sistema ahora incluye tanto salas físicas como equipos reservables.\n"
                "Los profesores pueden reservar:\n"
                "• Aulas y laboratorios\n"
                "• Videoproyectores portátiles\n" 
                "• Microscopios y equipos de laboratorio\n"
                "• Laptops y tablets para actividades móviles\n"
                "• Kits de robótica educativa\n"
                "• Equipos audiovisuales\n"
            )
        )
