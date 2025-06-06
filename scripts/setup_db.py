import os
import sys
import django

# Cambiar al directorio correcto del proyecto Django
project_django_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_django_root)
sys.path.insert(0, project_django_root)

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from rooms.models import Room, Reservation, Review
from django.contrib.auth import get_user_model
from django.db import transaction
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

print("\n" + "="*80)
print("=== EJECUTANDO LIMPIEZA Y REPOBLADO REAL ===")
print("="*80)

# PASO 1: LIMPIEZA COMPLETA
print("\n[PASO 1/3] LIMPIANDO DATOS EXISTENTES...")
print("-" * 50)

# Contar datos antes de limpiar
total_reviews_antes = Review.objects.count()
total_reservations_antes = Reservation.objects.count()
total_rooms_antes = Room.objects.count()

print(f"📊 Datos existentes ANTES de la limpieza:")
print(f"   - Reseñas: {total_reviews_antes}")
print(f"   - Reservas: {total_reservations_antes}")
print(f"   - Salas: {total_rooms_antes}")

# Limpiar datos
with transaction.atomic():
    Review.objects.all().delete()
    Reservation.objects.all().delete()
    Room.objects.all().delete()

print("🧹 ✅ Limpieza completada - Todos los datos eliminados")

# PASO 2: ACTUALIZAR FUNCIÓN crear_salas Y EJECUTAR
print("\n[PASO 2/3] ACTUALIZANDO Y EJECUTANDO SETUP...")
print("-" * 50)

# Importar datos necesarios para la nueva función
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Datos para generación de salas (copiados de setup_db.py)
UBICACIONES = [
    'Edificio Central - Planta 1', 'Edificio Central - Planta 2', 
    'Biblioteca - Zona Sur', 'Biblioteca - Zona Norte', 
    'Pabellón de Ciencias - Planta Baja', 'Pabellón de Ciencias - Planta Alta',
    'Campus Norte - Edificio A', 'Campus Norte - Edificio B',
    'Campus Sur - Edificio C', 'Facultad de Ingeniería - Sector 1',
    'Facultad de Letras - Aula Magna', 'Centro de Estudios - Planta 3'
]

EQUIPOS = [
    'Proyector, pizarra blanca, marcadores',
    'Computadores (10), proyector, equipo de sonido',
    'Pizarra interactiva, proyector, webcam HD',
    'Mesa de conferencia, proyector, sistema de videoconferencia',
    'Pizarra blanca, cámaras de documentos',
    'Pantalla táctil, sistema de audio, micrófonos inalámbricos',
    'Proyector 4K, sistema de sonido Dolby',
    'Pizarra tradicional, proyector básico',
    'Pizarras blancas móviles (3), proyector LED',
    'Ordenador profesor, proyector, altavoces'
]

# NUEVA FUNCIÓN crear_salas_mejorada
def crear_salas_mejorada():
    """Crea salas con nombres específicos por rol para demostración clara"""
    
    salas_creadas = 0
    
    # Tipos de salas organizados por rol con nombres claros para demostración
    tipos_sala = [
        # Salas para ESTUDIANTES
        {
            'nombre_base': 'Sala Estudiantes',
            'descripcion': 'Espacio para estudio individual o en grupos pequeños - Solo estudiantes',
            'allowed_roles': ['estudiante', 'profesor'],
            'room_type': 'sala_estudio',
            'minimo': 4,
            'maximo': 6,
            'es_gratuita_posibilidad': 0.4
        },
        {
            'nombre_base': 'Sala Individual Estudiantes',
            'descripcion': 'Espacio privado para estudio personal - Acceso estudiantil',
            'allowed_roles': ['estudiante', 'profesor'],
            'room_type': 'sala_individual',
            'minimo': 2,
            'maximo': 3,
            'es_gratuita_posibilidad': 0.5
        },
        
        # Salas para PROFESORES
        {
            'nombre_base': 'Aula Profesores',
            'descripcion': 'Sala para clases regulares - Solo profesores',
            'allowed_roles': ['profesor'],
            'room_type': 'aula',
            'minimo': 3,
            'maximo': 5,
            'es_gratuita_posibilidad': 0.0
        },
        {
            'nombre_base': 'Sala Conferencias Profesores',
            'descripcion': 'Espacio para presentaciones y eventos académicos - Profesores',
            'allowed_roles': ['profesor', 'soporte'],
            'room_type': 'sala_reunion',
            'minimo': 2,
            'maximo': 3,
            'es_gratuita_posibilidad': 0.0
        },
        
        # Salas TÉCNICAS
        {
            'nombre_base': 'Laboratorio Técnico',
            'descripcion': 'Sala equipada con material especializado - Personal técnico',
            'allowed_roles': ['profesor', 'soporte'],
            'room_type': 'laboratorio',
            'minimo': 2,
            'maximo': 3,
            'es_gratuita_posibilidad': 0.0
        },
        {
            'nombre_base': 'Sala Multimedia Técnica',
            'descripcion': 'Equipada con tecnología audiovisual avanzada - Técnicos',
            'allowed_roles': ['profesor', 'estudiante', 'soporte'],
            'room_type': 'auditorio',
            'minimo': 1,
            'maximo': 2,
            'es_gratuita_posibilidad': 0.0
        },
        
        # Salas ADMINISTRATIVAS
        {
            'nombre_base': 'Sala Administradores',
            'descripcion': 'Sala de reuniones administrativas - Solo administradores',
            'allowed_roles': ['admin'],
            'room_type': 'sala_reunion',
            'minimo': 1,
            'maximo': 2,
            'es_gratuita_posibilidad': 0.0
        },
        {
            'nombre_base': 'Sala Servidor Admin',
            'descripcion': 'Sala de servidores y equipamiento crítico - Solo admin',
            'allowed_roles': ['admin'],
            'room_type': 'sala_servidor',
            'minimo': 1,
            'maximo': 1,
            'es_gratuita_posibilidad': 0.0
        }
    ]
    
    for tipo in tipos_sala:
        num_salas = random.randint(tipo['minimo'], tipo['maximo'])
        
        for i in range(num_salas):
            numero_sala = i + 1
            nombre = f"{tipo['nombre_base']} {numero_sala}"
            
            # Asegurar nombre único
            contador = 1
            nombre_original = nombre
            while Room.objects.filter(name=nombre).exists():
                nombre = f"{nombre_original} (V{contador})"
                contador += 1
            
            # Generar otros datos
            capacidad = random.randint(5, 40)
            ubicacion = random.choice(UBICACIONES)
            equipamiento = random.choice(EQUIPOS)
            
            # Determinar si es gratuita
            es_gratuita = random.random() < tipo['es_gratuita_posibilidad']
            tarifa_hora = 0 if es_gratuita else random.randint(1500, 3000)
            
            # Generar horarios
            hora_apertura = random.choice(['06:00:00', '07:00:00', '08:00:00'])
            hora_cierre = random.choice(['20:00:00', '21:00:00', '22:00:00'])
            
            try:
                sala = Room.objects.create(
                    name=nombre,
                    location=ubicacion,
                    capacity=capacidad,
                    hourly_rate=tarifa_hora,
                    description=f"{tipo['descripcion']} - {equipamiento}",
                    equipment=equipamiento,
                    opening_time=hora_apertura,
                    closing_time=hora_cierre,
                    room_type=tipo['room_type'],
                    allowed_roles=','.join(tipo['allowed_roles']),
                    is_active=True
                )
                
                salas_creadas += 1
                estado_gratuita = "(GRATUITA)" if es_gratuita else f"(${tarifa_hora}/h)"
                roles_str = ", ".join(tipo['allowed_roles'])
                print(f"   ✅ {nombre} {estado_gratuita} - Roles: {roles_str}")
                
            except Exception as e:
                print(f"   ❌ Error al crear sala {nombre}: {e}")
    
    return salas_creadas

# Ejecutar creación de salas con nueva estructura
with transaction.atomic():
    total_salas_creadas = crear_salas_mejorada()

print(f"\n📊 Total de salas creadas: {total_salas_creadas}")

# PASO 3: MOSTRAR RESULTADOS REALES
print("\n[PASO 3/3] MOSTRANDO RESULTADOS REALES...")
print("-" * 50)

# Contar salas por tipo
salas_estudiantes = Room.objects.filter(name__icontains='Estudiantes').count()
salas_profesores = Room.objects.filter(name__icontains='Profesores').count()
salas_tecnicas = Room.objects.filter(name__icontains='Técnico').count()
salas_admin = Room.objects.filter(name__icontains='Administradores').count() + Room.objects.filter(name__icontains='Admin').count()

print(f"\n🔍 DISTRIBUCIÓN REAL DE SALAS:")
print(f"   🎓 Salas para Estudiantes: {salas_estudiantes}")
print(f"   👨‍🏫 Salas para Profesores: {salas_profesores}")
print(f"   🔧 Salas Técnicas: {salas_tecnicas}")
print(f"   👨‍💼 Salas Administrativas: {salas_admin}")

print(f"\n📋 LISTADO COMPLETO DE SALAS CREADAS:")
for sala in Room.objects.all().order_by('name'):
    roles = sala.allowed_roles.replace(',', ', ')
    gratis = "(GRATUITA)" if sala.hourly_rate == 0 else f"(${sala.hourly_rate}/h)"
    print(f"   • {sala.name} {gratis} - Capacidad: {sala.capacity} - Roles: {roles}")

print(f"\n" + "="*80)
print("=== PROCESO COMPLETADO EXITOSAMENTE ===")
print("="*80)

print(f"\n✅ RESUMEN FINAL:")
print(f"   - Salas eliminadas: {total_rooms_antes}")
print(f"   - Salas creadas: {total_salas_creadas}")
print(f"   - Reservas eliminadas: {total_reservations_antes}")
print(f"   - Reseñas eliminadas: {total_reviews_antes}")

print(f"\n🎯 LISTO PARA DEMOSTRACIÓN:")
print("   - Los nombres de las salas ahora indican claramente qué roles pueden acceder")
print("   - Estudiantes verán solo salas con 'Estudiantes' en el nombre")
print("   - Profesores verán salas de estudiantes + sus propias salas")
print("   - Administradores verán todas las salas")