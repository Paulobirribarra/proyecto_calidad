"""
Script unificado para configurar la base de datos desde cero.

Este script realiza todas las operaciones necesarias para preparar la base de datos:
1. Asegura que exista la carpeta de logs
2. Realiza las migraciones de Django desde cero
3. Crea un superusuario
4. Crea usuarios con diversos roles
5. Crea salas de distintos tipos
6. Genera reservas aleatorias de prueba

Uso: python manage.py shell < scripts/setup_db.py
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction
import logging

# Configurar logging para el script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# Importar modelos necesarios
try:
    from rooms.models import Room, Reservation, Review
    User = get_user_model()
    logger.info("Modelos cargados correctamente")
except ImportError as e:
    logger.error(f"Error al cargar modelos: {e}")
    sys.exit(1)

# === CONFIGURACIÓN DE DATOS PARA GENERACIÓN ===

# Datos para generación de usuarios
NOMBRES = [
    'Pablo', 'María', 'Juan', 'Ana', 'Carlos', 'Laura', 'Pedro', 'Sofía', 
    'Luisa', 'Miguel', 'Isabel', 'Diego', 'Carmen', 'José', 'Gabriela', 
    'Francisco', 'Valentina', 'Andrés', 'Fernanda', 'Alberto', 'Patricia'
]

APELLIDOS = [
    'Barra', 'López', 'García', 'Martínez', 'Rodríguez', 'González', 'Pérez',
    'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Díaz', 'Hernández', 'Morales', 
    'Vargas', 'Reyes', 'Castro', 'Ortega', 'Silva', 'Mendoza', 'Fuentes'
]

# Datos para generación de salas
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

# Propósitos para reservas
PROPOSITOS = [
    'Estudio individual',
    'Estudio grupal',
    'Reunión de proyecto',
    'Reunión de equipo docente',
    'Clase particular',
    'Tutoría',
    'Trabajo en grupo',
    'Videoconferencia',
    'Práctica de laboratorio',
    'Preparación de examen',
    'Presentación de proyecto',
    'Investigación',
    'Lectura y documentación',
    'Entrevista',
    'Sesión de estudio',
]

# === FUNCIONES AUXILIARES ===

def crear_directorio_logs():
    """Asegura que existe la carpeta logs para funcionamiento correcto"""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"✓ Directorio de logs creado en {logs_dir}")
    else:
        print(f"✓ Directorio de logs ya existe en {logs_dir}")

def generar_nombre_usuario(nombre, apellido):
    """Genera un nombre de usuario en formato inicial.apellido"""
    return f"{nombre[0].lower()}.{apellido.lower()}"

def generar_email(nombre, apellido):
    """Genera un email en formato nombre.apellido@colegio.cl"""
    return f"{nombre.lower()}.{apellido.lower()}@colegio.cl"

def generar_fecha_aleatoria(dias_futuro_max=30):
    """Genera una fecha aleatoria entre hoy y X días en el futuro"""
    hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dias_aleatorios = random.randint(1, dias_futuro_max)
    fecha_base = hoy + timedelta(days=dias_aleatorios)
    
    # Asegurar que la hora esté dentro del horario habitual (8-22)
    hora = random.randint(8, 21)
    minutos = random.choice([0, 30])  # Reservas en horas o medias horas
    return fecha_base.replace(hour=hora, minute=minutos)

# === FUNCIONES PRINCIPALES ===

def crear_superusuario():
    """Crea un superusuario para administración"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin', 
            password='admin123', 
            email='admin@example.com',
            first_name='Administrador',
            last_name='Sistema',
            role='admin'
        )
        print("✓ Superusuario 'admin' creado (contraseña: admin123)")
    else:
        print("✓ El superusuario 'admin' ya existe")

def crear_usuarios(cantidad=50):
    """Crea usuarios con diferentes roles"""
    
    # Distribución de roles
    roles = ['profesor', 'estudiante', 'soporte']
    distribucion = {
        'profesor': int(cantidad * 0.3),  # 30% profesores
        'estudiante': int(cantidad * 0.6),  # 60% estudiantes
        'soporte': max(cantidad - int(cantidad * 0.3) - int(cantidad * 0.6), 1)  # El resto soporte técnico
    }
    
    # Asegurar contraseña común para pruebas
    contrasena = 'Usuario123'  
    
    usuarios_creados = 0
    
    # Crear usuarios predefinidos para pruebas
    predefinidos = [
        ('profesor1', 'profesor2023', 'Juan', 'Pérez', 'juan.perez@colegio.cl', 'profesor'),
        ('estudiante1', 'estudiante2023', 'Ana', 'García', 'ana.garcia@colegio.cl', 'estudiante'),
        ('soporte1', 'soporte2023', 'Carlos', 'Rodríguez', 'carlos.rodriguez@colegio.cl', 'soporte')
    ]
    
    for username, password, nombre, apellido, email, rol in predefinidos:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=nombre,
                last_name=apellido,
                role=rol,
                terms_accepted=True,
                email_notifications=True
            )
            logger.info(f"Usuario predefinido creado: {username} ({rol})")
            usuarios_creados += 1
        else:
            logger.info(f"El usuario predefinido {username} ya existe")
    
    # Crear usuarios aleatorios para cada rol
    for rol, cantidad_rol in distribucion.items():
        for _ in range(cantidad_rol):
            nombre = random.choice(NOMBRES)
            apellido = random.choice(APELLIDOS)
            
            # Generar username único
            username_base = generar_nombre_usuario(nombre, apellido)
            username = username_base
            contador = 1
            
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{contador}"
                contador += 1
            
            # Crear usuario
            email = generar_email(nombre, apellido)
            
            # Verificar si el email ya existe
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=username,
                    password=contrasena,
                    email=email,
                    first_name=nombre,
                    last_name=apellido,
                    role=rol,
                    terms_accepted=True,
                    email_notifications=random.choice([True, False])
                )
                
                # Agregar teléfono para algunos usuarios
                if random.random() < 0.7:  # 70% de usuarios con teléfono
                    user.phone_number = f"+569 {random.randint(10000000, 99999999)}"
                    user.save()
                
                usuarios_creados += 1
            else:
                logger.info(f"Email duplicado: {email}, se omite el usuario")
    
    logger.info(f"Total de usuarios creados: {usuarios_creados}")

def crear_salas(cantidad=20):
    """Crea salas de diferentes tipos con distintos permisos"""
    
    salas_creadas = 0
      # Tipos de salas y sus permisos
    tipos_sala = [
        {
            'nombre': 'Aula estándar',
            'descripcion': 'Sala para clases regulares con capacidad media',
            'allowed_roles': ['profesor'],
            'room_type': 'aula',
            'minimo': 3,
            'maximo': 7
        },
        {
            'nombre': 'Laboratorio',
            'descripcion': 'Sala equipada con material especializado para prácticas',
            'allowed_roles': ['profesor', 'soporte'],
            'room_type': 'laboratorio',
            'minimo': 2,
            'maximo': 5
        },
        {
            'nombre': 'Sala de estudio',
            'descripcion': 'Espacio para estudio individual o en grupos pequeños',
            'allowed_roles': ['estudiante', 'profesor'],
            'room_type': 'sala_estudio',
            'minimo': 5,
            'maximo': 10
        },
        {
            'nombre': 'Sala individual',
            'descripcion': 'Espacio privado para estudio personal o reuniones pequeñas',
            'allowed_roles': ['estudiante', 'profesor'],
            'room_type': 'sala_individual',
            'minimo': 3,
            'maximo': 5
        },
        {
            'nombre': 'Sala de conferencias',
            'descripcion': 'Espacio para presentaciones y eventos',
            'allowed_roles': ['profesor', 'soporte'],
            'room_type': 'sala_reunion',
            'minimo': 1,
            'maximo': 3
        },
        {
            'nombre': 'Sala multimedia',
            'descripcion': 'Equipada con tecnología audiovisual avanzada',
            'allowed_roles': ['profesor', 'estudiante', 'soporte'],
            'room_type': 'auditorio',
            'minimo': 2,
            'maximo': 5
        },
        {
            'nombre': 'Laboratorio informático',
            'descripcion': 'Espacio con computadoras y software especializado',
            'allowed_roles': ['profesor', 'soporte'],
            'room_type': 'laboratorio',
            'minimo': 1,
            'maximo': 3
        }
    ]
    
    for tipo in tipos_sala:
        # Determinar cuántas salas de este tipo crear (distribución aleatoria)
        num_salas = random.randint(tipo['minimo'], tipo['maximo'])
        
        for i in range(num_salas):
            # Generar datos de la sala
            numero_sala = f"{random.choice('ABCDEFGH')}-{random.randint(100, 499)}"
            capacidad = random.randint(10, 50)
            ubicacion = random.choice(UBICACIONES)
            equipamiento = random.choice(EQUIPOS)
            
            # Crear nombre único para la sala
            nombre_base = f"{tipo['nombre']} {numero_sala}"
            nombre = nombre_base
            contador = 1
            
            while Room.objects.filter(name=nombre).exists():
                nombre = f"{nombre_base} ({contador})"
                contador += 1
            
            # Determinar si es gratuita o no (solo para salas de estudio)
            es_gratuita = tipo['nombre'] == 'Sala de estudio' and random.random() < 0.3
            tarifa_hora = 0 if es_gratuita else random.choice([1500, 2000, 2500, 3000])
              # Crear la sala
            room = Room.objects.create(
                name=nombre,
                description=f"{tipo['descripcion']} ubicada en {ubicacion}.",
                capacity=capacidad,
                location=ubicacion,
                equipment=equipamiento,
                is_active=True,
                hourly_rate=tarifa_hora,
                allowed_roles=','.join(tipo['allowed_roles']),
                room_type=tipo['room_type']
            )
            
            # Configurar horarios disponibles (generalmente 8am-10pm)
            room.opening_time = '08:00'
            room.closing_time = '22:00'
            room.save()
            
            salas_creadas += 1
            
    logger.info(f"Total de salas creadas: {salas_creadas}")

def generar_reservas(cantidad_por_usuario=3):
    """Genera reservas aleatorias respetando permisos por rol"""
    
    usuarios = User.objects.filter(is_active=True).exclude(is_superuser=True)
    reservas_creadas = 0
    reservas_fallidas = 0
    
    for user in usuarios:
        salas_disponibles = []
        
        # Obtener salas a las que este usuario tiene acceso según su rol
        for sala in Room.objects.filter(is_active=True):
            if user.role in sala.allowed_roles:
                salas_disponibles.append(sala)
        
        if not salas_disponibles:
            continue
            
        # Generar reservas para este usuario
        intentos_maximos = cantidad_por_usuario * 3  # Permitir algunos intentos extras
        intentos = 0
        reservas_usuario = 0
        
        while reservas_usuario < cantidad_por_usuario and intentos < intentos_maximos:
            intentos += 1
            sala = random.choice(salas_disponibles)
            fecha_inicio = generar_fecha_aleatoria()
            
            # Duración aleatoria entre 1 y 3 horas
            duracion_horas = random.choice([1, 1.5, 2, 3])
            fecha_fin = fecha_inicio + timedelta(hours=duracion_horas)
            
            # Verificar disponibilidad (no necesita ser perfecta para datos de prueba)
            reservas_existentes = Reservation.objects.filter(
                room=sala,
                end_time__gt=fecha_inicio,
                start_time__lt=fecha_fin,
                status__in=['confirmed', 'pending']
            )
            if reservas_existentes.exists():
                continue  # Sala ocupada, intentar otra fecha
                
            # Crear reserva
            try:
                proposito = random.choice(PROPOSITOS)
                num_personas = random.randint(1, min(5, sala.capacity))
                reservation = Reservation.objects.create(
                    user=user,
                    room=sala,
                    start_time=fecha_inicio,
                    end_time=fecha_fin,
                    purpose=proposito,
                    attendees_count=num_personas,
                    status=random.choice(['confirmed', 'pending']),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 7))
                )
                
                # Agregar una reseña a algunas reservas (para histórico)
                if random.random() < 0.3:  # 30% de reservas con reseña
                    # Marcar como que ya sucedió y fue completada
                    historic_start = timezone.now() - timedelta(days=random.randint(10, 30))
                    historic_end = historic_start + timedelta(hours=duracion_horas)
                    
                    reservation.start_time = historic_start
                    reservation.end_time = historic_end
                    reservation.status = 'completed'
                    reservation.save()
                    # Crear la reseña
                    puntuacion = random.randint(3, 5)  # Mayoría positivas para datos de demo
                    comentarios = [
                        "Excelente sala, muy bien equipada.",
                        "Todo funcionó perfectamente.",
                        "Buena iluminación y equipamiento.",
                        "Ambiente tranquilo para estudiar.",
                        "La ubicación es muy conveniente.",
                        "Volvería a reservar sin dudas.",
                        "Experiencia satisfactoria.",
                        "La sala cumplió con mis necesidades."
                    ]
                    
                    # Tipos de comentarios
                    tipos_comentarios = ['positive', 'suggestion', 'problem', 'neutral']
                    
                    # Crear calificaciones específicas (con ligeras variaciones)
                    limpieza = max(1, min(5, puntuacion + random.choice([-1, 0, 0, 1])))
                    equipamiento = max(1, min(5, puntuacion + random.choice([-1, 0, 0, 1])))
                    comodidad = max(1, min(5, puntuacion + random.choice([-1, 0, 0, 1])))
                    
                    Review.objects.create(
                        reservation=reservation,
                        rating=puntuacion,
                        comment=random.choice(comentarios),
                        comment_type=random.choice(tipos_comentarios),
                        cleanliness_rating=limpieza,
                        equipment_rating=equipamiento,
                        comfort_rating=comodidad,
                        created_at=historic_end + timedelta(hours=random.randint(1, 48))
                    )
                
                reservas_creadas += 1
                reservas_usuario += 1
                
            except Exception as e:
                logger.warning(f"Error al crear reserva: {e}")
                reservas_fallidas += 1
    
    logger.info(f"Reservas creadas: {reservas_creadas} (fallidas: {reservas_fallidas})")

# === FUNCIÓN PRINCIPAL ===

def configurar_base_datos():
    """Función principal para configurar la base de datos desde cero"""
    
    try:
        print("\n" + "=" * 80)
        print("=== INICIANDO CONFIGURACIÓN DE BASE DE DATOS ===")
        print("=" * 80 + "\n")
        
        # Paso 1: Crear directorio de logs
        print("[1/5] Creando directorio de logs...")
        crear_directorio_logs()
        
        # Paso 2: Crear superusuario
        print("\n[2/5] Creando superusuario...")
        crear_superusuario()
        
        # Paso 3: Crear usuarios
        print("\n[3/5] Creando usuarios con diferentes roles...")
        with transaction.atomic():
            crear_usuarios(30)  # Crear 30 usuarios aleatorios más los predefinidos
        
        # Paso 4: Crear salas
        print("\n[4/5] Creando salas de diferentes tipos...")
        with transaction.atomic():
            crear_salas(20)  # Crear alrededor de 20 salas aproximadamente
        
        # Paso 5: Generar reservas
        print("\n[5/5] Generando reservas aleatorias...")
        with transaction.atomic():
            generar_reservas(3)  # ~3 reservas por usuario en promedio
        
        print("\n" + "=" * 80)
        print("=== CONFIGURACIÓN DE BASE DE DATOS COMPLETADA CON ÉXITO ===")
        print("=" * 80 + "\n")
        
        print("USUARIOS DE PRUEBA:")
        print("- Admin: admin / admin123")
        print("- Profesor: profesor1 / profesor2023")
        print("- Estudiante: estudiante1 / estudiante2023")
        print("- Soporte: soporte1 / soporte2023")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("La configuración de la base de datos falló.")
        raise

if __name__ == "__main__":
    configurar_base_datos()
