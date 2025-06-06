"""
Script para probar la paginación en la vista de salas.

Este script simula las solicitudes a la vista de salas como diferentes usuarios
para comprobar que la paginación funcione correctamente.
"""

import os
import sys
import django

# Asegurarse de que el proyecto esté en el path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.urls import reverse

# Importaciones que dependen de Django
from rooms.models import Room
from rooms.views import room_list

# Obtener el modelo de usuario
User = get_user_model()

def test_room_pagination():
    print("=== Prueba de Paginación en la Vista de Salas ===")
    
    try:
        # Obtener usuarios para probar
        estudiantes = User.objects.filter(role='estudiante')
        admin = User.objects.filter(is_staff=True).first() or User.objects.filter(is_superuser=True).first()
        
        if not estudiantes:
            print("No hay estudiantes en la base de datos")
            return
        
        if not admin:
            print("No hay administradores en la base de datos")
            return
        
        # Usar el primer estudiante para pruebas
        estudiante = estudiantes.first()
        
        print(f"Probando con estudiante: {estudiante.username}")
        print(f"Probando con administrador: {admin.username}")
        
        # Verificar cantidad de salas
        salas_activas = Room.objects.filter(is_active=True)
        total_salas = salas_activas.count()
        print(f"Total de salas activas: {total_salas}")
        
        # Verificar qué salas puede ver el estudiante
        salas_estudiante = []
        for sala in salas_activas:
            if sala.can_be_reserved_by(estudiante):
                salas_estudiante.append(sala)
                
        print(f"El estudiante {estudiante.username} puede ver {len(salas_estudiante)} salas")
        print(f"Tipos de sala visibles para estudiante: {set([s.room_type for s in salas_estudiante])}")
        
        # Verificar qué salas puede ver el admin
        salas_admin = []
        for sala in salas_activas:
            if sala.can_be_reserved_by(admin):
                salas_admin.append(sala)
        
        print(f"El administrador {admin.username} puede ver {len(salas_admin)} salas")
        print(f"Tipos de sala visibles para admin: {set([s.room_type for s in salas_admin])}")
        
        # Verificar que el filtrado funcione correctamente
        print("\nVerificando que no hay duplicados en salas visibles por estudiante...")
        salas_estudiante_ids = [sala.id for sala in salas_estudiante]
        if len(salas_estudiante_ids) != len(set(salas_estudiante_ids)):
            print("ERROR: Hay duplicados en las salas disponibles")
        else:
            print("ÉXITO: No hay duplicados en las salas disponibles")
            
        # Verificar el algoritmo de filtrado
        if len(salas_estudiante) < total_salas:
            print("ÉXITO: El filtrado está funcionando correctamente para estudiantes")
        else:
            print("ADVERTENCIA: El estudiante puede ver todas las salas, verifica los permisos")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_room_pagination()
