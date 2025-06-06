"""
Script para poblar la base de datos con usuarios de diferentes roles.

Este script crea usuarios de demostración para cada rol del sistema:
- admin: Administradores del sistema
- profesor: Profesores que pueden reservar cualquier sala
- estudiante: Estudiantes con acceso limitado
- soporte: Personal de soporte técnico

Ejecutar: python manage.py shell < scripts/setup_users.py
"""

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

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
import random

User = get_user_model()

print("\n" + "="*80)
print("=== CREANDO USUARIOS DE DEMOSTRACIÓN ===")
print("="*80)

# PASO 1: MOSTRAR USUARIOS EXISTENTES
print("\n[PASO 1/3] VERIFICANDO USUARIOS EXISTENTES...")
print("-" * 50)

usuarios_existentes = User.objects.count()
if usuarios_existentes > 0:
    print(f"📊 Usuarios existentes: {usuarios_existentes}")
    for user in User.objects.all().order_by('role', 'username'):
        print(f"   • {user.username} ({user.get_role_display()}) - {user.email}")
    
    respuesta = input("\n¿Deseas eliminar usuarios existentes? (y/N): ").lower()
    if respuesta == 'y':
        User.objects.all().delete()
        print("🧹 ✅ Usuarios eliminados")
else:
    print("📊 No hay usuarios existentes")

# PASO 2: CREAR USUARIOS DE DEMOSTRACIÓN
print("\n[PASO 2/3] CREANDO USUARIOS DE DEMOSTRACIÓN...")
print("-" * 50)

# Datos base para usuarios - nombres aleatorios pero usernames predecibles
nombres_ejemplos = [
    'María', 'José', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Elena', 'Miguel',
    'Isabel', 'Antonio', 'Lucía', 'Francisco', 'Rosa', 'Manuel', 'Pilar',
    'David', 'Cristina', 'Javier', 'Mónica', 'Carlos'
]
apellidos_ejemplos = [
    'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez',
    'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández',
    'Díaz', 'Moreno', 'Álvarez', 'Muñoz', 'Romero', 'Alonso', 'Gutiérrez'
]

def generar_nombre_completo():
    """Genera un nombre completo aleatorio"""
    nombre = random.choice(nombres_ejemplos)
    apellido1 = random.choice(apellidos_ejemplos)
    apellido2 = random.choice(apellidos_ejemplos)
    return nombre, f"{apellido1} {apellido2}"

def crear_usuario(username, email, role, first_name, last_name, is_staff=False, is_superuser=False):
    """Crea un usuario con los datos especificados"""
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password='demo123',  # Contraseña simple para demostración
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True,
            terms_accepted=True,
            email_notifications=True,
            phone_number=f"+569{random.randint(10000000, 99999999)}"
        )
        return user
    except IntegrityError as e:
        print(f"   ❌ Error al crear {username}: {e}")
        return None

usuarios_creados = 0

# ADMINISTRADOR (Solo 1)
print("\n🔧 Creando Administrador...")
nombre, apellidos = generar_nombre_completo()
user = crear_usuario('admin', 'admin@universidad.edu', 'admin', nombre, apellidos, 
                    is_staff=True, is_superuser=True)
if user:
    usuarios_creados += 1
    print(f"   ✅ admin - {user.email} (Admin/Staff/Superuser)")
    print(f"      Nombre: {user.first_name} {user.last_name}")

# PROFESORES (Máximo 3)
print("\n👨‍🏫 Creando Profesores...")
for i in range(1, 4):  # profesor1, profesor2, profesor3
    nombre, apellidos = generar_nombre_completo()
    username = f"profesor{i}"
    email = f"profesor{i}@profesores.edu"
    
    user = crear_usuario(username, email, 'profesor', f"Dr. {nombre}", apellidos)
    if user:
        usuarios_creados += 1
        print(f"   ✅ {username} - {email}")
        print(f"      Nombre: {user.first_name} {user.last_name}")

# ESTUDIANTES (Máximo 3)
print("\n🎓 Creando Estudiantes...")
for i in range(1, 4):  # estudiante1, estudiante2, estudiante3
    nombre, apellidos = generar_nombre_completo()
    username = f"estudiante{i}"
    email = f"estudiante{i}@estudiantes.edu"
    
    user = crear_usuario(username, email, 'estudiante', nombre, apellidos)
    if user:
        usuarios_creados += 1
        print(f"   ✅ {username} - {email}")
        print(f"      Nombre: {user.first_name} {user.last_name}")

# PERSONAL DE SOPORTE (Máximo 3)
print("\n🔧 Creando Personal de Soporte...")
for i in range(1, 4):  # soporte1, soporte2, soporte3
    nombre, apellidos = generar_nombre_completo()
    username = f"soporte{i}"
    email = f"soporte{i}@universidad.edu"
    
    user = crear_usuario(username, email, 'soporte', nombre, apellidos)
    if user:
        usuarios_creados += 1
        print(f"   ✅ {username} - {email}")
        print(f"      Nombre: {user.first_name} {user.last_name}")

# PASO 3: MOSTRAR RESULTADOS
print("\n[PASO 3/3] RESUMEN DE USUARIOS CREADOS...")
print("-" * 50)

# Contar usuarios por rol
admins = User.objects.filter(role='admin').count()
profesores = User.objects.filter(role='profesor').count()
estudiantes = User.objects.filter(role='estudiante').count()
soporte = User.objects.filter(role='soporte').count()

print(f"\n📊 DISTRIBUCIÓN DE USUARIOS:")
print(f"   🔧 Administradores: {admins}")
print(f"   👨‍🏫 Profesores: {profesores}")
print(f"   🎓 Estudiantes: {estudiantes}")
print(f"   🛠️ Soporte Técnico: {soporte}")
print(f"   📈 TOTAL: {usuarios_creados}")

print(f"\n📋 LISTADO COMPLETO DE USUARIOS:")
for user in User.objects.all().order_by('role', 'username'):
    staff_info = " (Staff)" if user.is_staff else ""
    super_info = " (Superuser)" if user.is_superuser else ""
    print(f"   • {user.username} - {user.get_role_display()}{staff_info}{super_info}")
    print(f"     Email: {user.email} | Nombre: {user.first_name} {user.last_name}")

print(f"\n" + "="*80)
print("=== USUARIOS CREADOS EXITOSAMENTE ===")
print("="*80)

print(f"\n🔑 CREDENCIALES DE ACCESO:")
print("   Username: [cualquier usuario de arriba]")
print("   Password: demo123")

print(f"\n🎯 USUARIOS PARA PRUEBAS RÁPIDAS:")
print("   👨‍💼 Admin: admin / demo123")
print("   👨‍🏫 Profesor: profesor1 / demo123")
print("   🎓 Estudiante: estudiante1 / demo123")
print("   🛠️ Soporte: soporte1 / demo123")

print(f"\n✅ ¡Configuración completa! Ya puedes hacer login con cualquier usuario.")
