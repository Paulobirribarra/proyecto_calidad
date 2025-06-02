"""
Script para poblar la base de datos con usuarios de distintos roles.

Este script crea usuarios con roles de profesor, estudiante y soporte técnico
con un formato de correo electrónico específico (nombre.apellido@colegio.cl).

Se debe ejecutar con: python manage.py shell < populate_users.py
"""

import os
import django
import random

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rooms.models import Room

User = get_user_model()

# Nombres y apellidos para generar usuarios aleatorios
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

def generar_nombre_usuario(nombre, apellido):
    """Genera un nombre de usuario en formato inicial.apellido"""
    return f"{nombre[0].lower()}.{apellido.lower()}"

def generar_email(nombre, apellido):
    """Genera un email en formato nombre.apellido@colegio.cl"""
    return f"{nombre.lower()}.{apellido.lower()}@colegio.cl"

def crear_usuarios(cantidad=50):
    """Crea usuarios con diferentes roles"""
    
    usuarios_creados = []
    roles = ['profesor', 'estudiante', 'soporte']
    
    print(f"Creando {cantidad} usuarios...")
    
    for _ in range(cantidad):
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        username = generar_nombre_usuario(nombre, apellido)
        email = generar_email(nombre, apellido)
        rol = random.choice(roles)
        
        # Evitar nombres de usuario duplicados
        i = 1
        temp_username = username
        while User.objects.filter(username=temp_username).exists():
            temp_username = f"{username}{i}"
            i += 1
        username = temp_username
        
        # Evitar emails duplicados
        i = 1
        temp_email = email
        while User.objects.filter(email=temp_email).exists():
            temp_email = f"{nombre.lower()}.{apellido.lower()}{i}@colegio.cl"
            i += 1
        email = temp_email
        
        # Crear usuario
        password = 'password123'  # En producción usar passwords seguros
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido,
                role=rol,
                terms_accepted=True
            )
            
            # Agregar teléfono para algunos usuarios
            if random.random() > 0.5:
                user.phone_number = f"+569{random.randint(10000000, 99999999)}"
                user.save()
            
            usuarios_creados.append(user)
            print(f"Usuario creado: {username} ({email}) - Rol: {rol}")
        except Exception as e:
            print(f"Error al crear usuario {username}: {e}")
    
    return usuarios_creados

def crear_usuarios_específicos():
    """Crea usuarios específicos para cada rol"""
    
    usuarios_específicos = [
        # Profesores
        {'nombre': 'Carmen', 'apellido': 'Morales', 'rol': 'profesor'},
        {'nombre': 'Roberto', 'apellido': 'Gómez', 'rol': 'profesor'},
        {'nombre': 'Claudia', 'apellido': 'Vega', 'rol': 'profesor'},
        {'nombre': 'Felipe', 'apellido': 'Muñoz', 'rol': 'profesor'},
        {'nombre': 'Lorena', 'apellido': 'Ponce', 'rol': 'profesor'},
        
        # Estudiantes
        {'nombre': 'Daniela', 'apellido': 'Torres', 'rol': 'estudiante'},
        {'nombre': 'Sebastián', 'apellido': 'Rojas', 'rol': 'estudiante'},
        {'nombre': 'Valentina', 'apellido': 'Lagos', 'rol': 'estudiante'},
        {'nombre': 'Matías', 'apellido': 'Fuentes', 'rol': 'estudiante'},
        {'nombre': 'Camila', 'apellido': 'Soto', 'rol': 'estudiante'},
        
        # Soporte técnico
        {'nombre': 'Ricardo', 'apellido': 'Paredes', 'rol': 'soporte'},
        {'nombre': 'Andrea', 'apellido': 'Valenzuela', 'rol': 'soporte'},
        {'nombre': 'Ignacio', 'apellido': 'Molina', 'rol': 'soporte'},
    ]
    
    usuarios_creados = []
    
    print("Creando usuarios específicos...")
    
    for datos in usuarios_específicos:
        nombre = datos['nombre']
        apellido = datos['apellido']
        username = generar_nombre_usuario(nombre, apellido)
        email = generar_email(nombre, apellido)
        rol = datos['rol']
        
        # Evitar nombres de usuario duplicados
        i = 1
        temp_username = username
        while User.objects.filter(username=temp_username).exists():
            temp_username = f"{username}{i}"
            i += 1
        username = temp_username
        
        # Evitar emails duplicados
        i = 1
        temp_email = email
        while User.objects.filter(email=temp_email).exists():
            temp_email = f"{nombre.lower()}.{apellido.lower()}{i}@colegio.cl"
            i += 1
        email = temp_email
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=nombre,
                last_name=apellido,
                role=rol,
                terms_accepted=True
            )
            
            # Agregar teléfono
            user.phone_number = f"+569{random.randint(10000000, 99999999)}"
            user.save()
            
            usuarios_creados.append(user)
            print(f"Usuario específico creado: {username} ({email}) - Rol: {rol}")
        except Exception as e:
            print(f"Error al crear usuario específico {username}: {e}")
    
    return usuarios_creados

if __name__ == '__main__':
    # Verificar si ya existen suficientes usuarios
    if User.objects.count() > 10:
        print(f"Ya hay {User.objects.count()} usuarios en la base de datos.")
        respuesta = input("¿Desea crear más usuarios? (s/n): ")
        if respuesta.lower() != 's':
            print("Operación cancelada.")
            exit()
    
    # Crear usuarios específicos
    usuarios_específicos = crear_usuarios_específicos()
    
    # Crear usuarios aleatorios
    cantidad_aleatorios = 20  # Puedes ajustar este número
    usuarios_aleatorios = crear_usuarios(cantidad_aleatorios)
    
    # Mostrar resumen
    print("\nResumen de usuarios creados:")
    print(f"Usuarios específicos: {len(usuarios_específicos)}")
    print(f"Usuarios aleatorios: {len(usuarios_aleatorios)}")
    
    # Mostrar estadísticas por rol
    profesores = User.objects.filter(role='profesor').count()
    estudiantes = User.objects.filter(role='estudiante').count()
    soporte = User.objects.filter(role='soporte').count()
    admin = User.objects.filter(role='admin').count()
    
    print("\nDistribución por roles:")
    print(f"- Profesores: {profesores}")
    print(f"- Estudiantes: {estudiantes}")
    print(f"- Soporte Técnico: {soporte}")
    print(f"- Administradores: {admin}")
    print("\nTodos los usuarios tienen la contraseña: password123")
