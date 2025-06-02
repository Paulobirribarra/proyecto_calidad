"""
Script simplificado para crear usuarios de prueba con diferentes roles
"""
import os
import django
import random

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importaciones específicas
from django.contrib.auth import get_user_model
User = get_user_model()

# Datos de prueba
profesores = [
    {'nombre': 'Carmen', 'apellido': 'Morales', 'email': 'c.morales@colegio.cl'},
    {'nombre': 'Roberto', 'apellido': 'Gómez', 'email': 'r.gomez@colegio.cl'},
    {'nombre': 'Claudia', 'apellido': 'Vega', 'email': 'c.vega@colegio.cl'},
    {'nombre': 'Felipe', 'apellido': 'Muñoz', 'email': 'f.munoz@colegio.cl'},
    {'nombre': 'Lorena', 'apellido': 'Ponce', 'email': 'l.ponce@colegio.cl'},
]

estudiantes = [
    {'nombre': 'Daniela', 'apellido': 'Torres', 'email': 'd.torres@colegio.cl'},
    {'nombre': 'Sebastián', 'apellido': 'Rojas', 'email': 's.rojas@colegio.cl'},
    {'nombre': 'Valentina', 'apellido': 'Lagos', 'email': 'v.lagos@colegio.cl'},
    {'nombre': 'Matías', 'apellido': 'Fuentes', 'email': 'm.fuentes@colegio.cl'},
    {'nombre': 'Camila', 'apellido': 'Soto', 'email': 'c.soto@colegio.cl'},
]

soporte = [
    {'nombre': 'Ricardo', 'apellido': 'Paredes', 'email': 'r.paredes@colegio.cl'},
    {'nombre': 'Andrea', 'apellido': 'Valenzuela', 'email': 'a.valenzuela@colegio.cl'},
    {'nombre': 'Ignacio', 'apellido': 'Molina', 'email': 'i.molina@colegio.cl'},
]

def crear_usuarios():
    print("Creando usuarios de prueba...")
    
    # Crear usuarios profesores
    for profesor in profesores:
        try:
            username = profesor['email'].split('@')[0]
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=profesor['email'],
                    password='password123',
                    first_name=profesor['nombre'],
                    last_name=profesor['apellido'],
                    role='profesor',
                    is_active=True,
                    terms_accepted=True
                )
                print(f"Profesor creado: {user.username} ({user.email})")
            else:
                print(f"El usuario {username} ya existe.")
        except Exception as e:
            print(f"Error al crear profesor {profesor['email']}: {e}")
    
    # Crear usuarios estudiantes
    for estudiante in estudiantes:
        try:
            username = estudiante['email'].split('@')[0]
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=estudiante['email'],
                    password='password123',
                    first_name=estudiante['nombre'],
                    last_name=estudiante['apellido'],
                    role='estudiante',
                    is_active=True,
                    terms_accepted=True
                )
                print(f"Estudiante creado: {user.username} ({user.email})")
            else:
                print(f"El usuario {username} ya existe.")
        except Exception as e:
            print(f"Error al crear estudiante {estudiante['email']}: {e}")
    
    # Crear usuarios soporte
    for tecnico in soporte:
        try:
            username = tecnico['email'].split('@')[0]
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=tecnico['email'],
                    password='password123',
                    first_name=tecnico['nombre'],
                    last_name=tecnico['apellido'],
                    role='soporte',
                    is_active=True,
                    terms_accepted=True
                )
                print(f"Soporte creado: {user.username} ({user.email})")
            else:
                print(f"El usuario {username} ya existe.")
        except Exception as e:
            print(f"Error al crear soporte {tecnico['email']}: {e}")
    
    # Crear un usuario administrador si no existe
    if not User.objects.filter(username='administrador').exists():
        try:
            User.objects.create_user(
                username='administrador',
                email='admin@colegio.cl',
                password='admin123',
                first_name='Admin',
                last_name='Sistema',
                role='admin',
                is_active=True,
                is_staff=True,
                is_superuser=True,
                terms_accepted=True
            )
            print("Administrador creado: administrador (admin@colegio.cl)")
        except Exception as e:
            print(f"Error al crear administrador: {e}")
    
    # Mostrar resumen
    print("\nResumen de usuarios en el sistema:")
    print(f"Total usuarios: {User.objects.count()}")
    for rol, nombre in User.ROLE_CHOICES:
        count = User.objects.filter(role=rol).count()
        print(f"- {nombre}: {count}")

if __name__ == "__main__":
    crear_usuarios()
