"""
Script para verificar el estado actual de la base de datos.
"""

import os
import sys
import django

# Añadir el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar modelos
from django.contrib.auth import get_user_model
from rooms.models import Room, Reservation, Review

User = get_user_model()

def mostrar_estadísticas():
    """Muestra estadísticas generales de la base de datos"""
    
    # Estadísticas de usuarios
    total_usuarios = User.objects.count()
    print(f"\nESTADÍSTICAS DE USUARIOS ({total_usuarios} total):")
    print("-" * 40)
    for rol, nombre in User.ROLE_CHOICES:
        count = User.objects.filter(role=rol).count()
        print(f"{nombre}: {count}")
    
    # Estadísticas de salas
    total_salas = Room.objects.count()
    print(f"\nESTADÍSTICAS DE SALAS ({total_salas} total):")
    print("-" * 40)
    for tipo, nombre in Room.ROOM_TYPE_CHOICES:
        count = Room.objects.filter(room_type=tipo).count()
        print(f"{nombre}: {count}")
    
    # Estadísticas de reservas
    total_reservas = Reservation.objects.count()
    print(f"\nESTADÍSTICAS DE RESERVAS ({total_reservas} total):")
    print("-" * 40)
    for estado, nombre in Reservation.STATUS_CHOICES:
        count = Reservation.objects.filter(status=estado).count()
        print(f"{nombre}: {count}")
    
    # Detalles por rol
    print("\nRESERVAS POR ROL DE USUARIO:")
    print("-" * 40)
    for rol, nombre in User.ROLE_CHOICES:
        count = Reservation.objects.filter(user__role=rol).count()
        print(f"{nombre}: {count}")
    
    # Mostrar algunos ejemplos
    print("\nALGUNOS USUARIOS CREADOS:")
    print("-" * 40)
    for user in User.objects.all()[:5]:
        print(f"- {user.username} ({user.email}) - Rol: {user.get_role_display()}")
    
    print("\nALGUNAS SALAS CREADAS:")
    print("-" * 40)
    for sala in Room.objects.all()[:5]:
        print(f"- {sala.name} - Tipo: {sala.get_room_type_display()}")
        print(f"  Permisos: {sala.allowed_roles}")
    
    print("\nALGUNAS RESERVAS CREADAS:")
    print("-" * 40)
    for reserva in Reservation.objects.all()[:5]:
        print(f"- {reserva.room.name} por {reserva.user.username} ({reserva.user.get_role_display()})")
        print(f"  {reserva.start_time.strftime('%d/%m/%Y %H:%M')} - Estado: {reserva.get_status_display()}")

if __name__ == "__main__":
    mostrar_estadísticas()
