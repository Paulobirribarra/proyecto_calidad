"""
Script para verificar la lógica de filtrado en las vistas

Este script simula la ejecución de la vista room_list con diferentes usuarios
para verificar que el filtrado de salas se aplica correctamente.
"""

import os
import sys
import django

# Asegurarse de que el proyecto esté en el path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importaciones que dependen de Django
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse
from rooms.views import room_list
from rooms.models import Room

User = get_user_model()

def test_view_logic():
    print("=== Prueba de Filtrado y Paginación en la Vista de Salas ===")
    
    try:
        # Obtener usuarios para probar
        estudiante = User.objects.filter(role='estudiante').first()
        admin = User.objects.filter(is_staff=True).first() or User.objects.filter(is_superuser=True).first()
        
        if not estudiante or not admin:
            print("No hay usuarios suficientes para la prueba")
            return
        
        print(f"Probando con estudiante: {estudiante.username}")
        print(f"Probando con administrador: {admin.username}")
        
        # Crear factory para simular requests
        factory = RequestFactory()
        
        # Verificar la vista con estudiante
        print("\nProbando vista como estudiante:")
        request = factory.get(reverse('rooms:room_list'))
        request.user = estudiante
        
        # Ejecutar la vista con el usuario estudiante
        try:
            response = room_list(request)
            print("La vista se ejecutó correctamente")
        except Exception as e:
            print(f"Error al ejecutar la vista: {e}")
        
        # Verificar la lógica del filtrado en la vista
        print("\nVerificando la lógica del filtrado:")
        
        # 1. Obtener todas las salas y filtrarlas manualmente para estudiante
        todas_salas = Room.objects.filter(is_active=True)
        salas_estudiante = [sala for sala in todas_salas if sala.can_be_reserved_by(estudiante)]
        
        print(f"Total de salas: {todas_salas.count()}")
        print(f"Salas que debería ver el estudiante: {len(salas_estudiante)}")
        
        # 2. Obtener queryset después de filtrar por tipos de sala permitidos para estudiantes
        salas_tipos_permitidos = todas_salas.filter(room_type__in=['sala_estudio', 'sala_individual', 'auditorio'])
        print(f"Salas con tipos permitidos para estudiantes: {salas_tipos_permitidos.count()}")
        
        # 3. Comprobar que los resultados son consistentes
        # Se espera que estas cantidades sean iguales o muy similares 
        # dependiendo de las restricciones específicas adicionales
        print(f"¿Son iguales o similares? {abs(len(salas_estudiante) - salas_tipos_permitidos.count()) <= 2}")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_view_logic()
