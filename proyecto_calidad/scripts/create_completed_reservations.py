#!/usr/bin/env python
"""
Script para crear reservas completadas para probar el sistema de valoración.

Este script crea reservas con fechas en el pasado y las marca como completadas
para que puedan ser calificadas por los usuarios.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from django.contrib.auth import get_user_model
from rooms.models import Room, Reservation

User = get_user_model()

def create_completed_reservations():
    """Crea reservas completadas para testing del sistema de valoración."""
    
    print("🚀 Iniciando creación de reservas completadas...")
    
    # Obtener usuarios existentes
    users = User.objects.all()[:5]  # Primeros 5 usuarios
    if not users:
        print("❌ Error: No hay usuarios en la base de datos.")
        print("💡 Ejecuta primero: python populate_users.py")
        return False
    
    # Obtener salas existentes
    rooms = Room.objects.filter(is_active=True)[:3]  # Primeras 3 salas activas
    if not rooms:
        print("❌ Error: No hay salas activas en la base de datos.")
        print("💡 Ejecuta primero: python populate_rooms.py")
        return False
    
    print(f"📊 Usuarios disponibles: {len(users)}")
    print(f"🏢 Salas disponibles: {len(rooms)}")
    
    completed_reservations = []
    
    # Crear reservas completadas en los últimos 7 días
    for i, user in enumerate(users):
        for j, room in enumerate(rooms):
            try:
                # Fecha en el pasado (1-7 días atrás)
                days_ago = (i + j + 1) % 7 + 1
                start_date = timezone.now() - timedelta(days=days_ago)
                
                # Hora de inicio entre 9:00 y 16:00
                start_hour = 9 + (i + j) % 8
                start_time = start_date.replace(
                    hour=start_hour, 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
                
                # Duración de 1-3 horas
                duration_hours = 1 + (i + j) % 3
                end_time = start_time + timedelta(hours=duration_hours)
                
                # Verificar si ya existe una reserva similar
                existing = Reservation.objects.filter(
                    user=user,
                    room=room,
                    start_time=start_time
                ).first()
                
                if not existing:
                    # Crear la reserva
                    reservation = Reservation.objects.create(
                        user=user,
                        room=room,
                        start_time=start_time,
                        end_time=end_time,
                        purpose=f"Sesión de estudio - Testing {i+1}-{j+1}",
                        status='completed'  # Marcar como completada directamente
                    )
                    
                    completed_reservations.append(reservation)
                    
                    print(f"✅ Reserva creada: {user.username} - {room.name}")
                    print(f"   📅 {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
                    
            except Exception as e:
                print(f"❌ Error creando reserva para {user.username} en {room.name}: {e}")
                continue
    
    print(f"\n🎉 ¡Script completado!")
    print(f"📈 Total de reservas completadas creadas: {len(completed_reservations)}")
    
    if completed_reservations:
        print(f"\n🔍 Ejemplos de reservas creadas:")
        for i, reservation in enumerate(completed_reservations[:3]):
            print(f"   {i+1}. ID: {reservation.id} | Usuario: {reservation.user.username} | Sala: {reservation.room.name}")
        
        print(f"\n🌟 Para probar el sistema de valoración:")
        print(f"   1. Inicia sesión con cualquiera de estos usuarios:")
        for user in users[:3]:
            print(f"      - {user.username}")
        print(f"   2. Ve a 'Mis Reservas'")
        print(f"   3. Busca reservas 'Completadas'")
        print(f"   4. Haz clic en '📝 Calificar'")
        
        # Mostrar URL directa para la primera reserva
        first_reservation = completed_reservations[0]
        print(f"\n🎯 URL directa para valorar:")
        print(f"   http://127.0.0.1:8000/salas/reservation/{first_reservation.id}/review/")
        print(f"   (Usuario: {first_reservation.user.username})")
    
    return True

def show_existing_completed_reservations():
    """Muestra las reservas completadas existentes."""
    
    completed_reservations = Reservation.objects.filter(status='completed')
    
    if not completed_reservations:
        print("❌ No hay reservas completadas en la base de datos.")
        return
    
    print(f"\n📋 Reservas completadas existentes ({len(completed_reservations)}):")
    print("-" * 80)
    
    for reservation in completed_reservations[:10]:  # Mostrar primeras 10
        has_review = hasattr(reservation, 'review')
        review_status = "Ya calificada" if has_review else "Pendiente de calificar"
        
        print(f"ID: {reservation.id:3d} | "
              f"Usuario: {reservation.user.username:15s} | "
              f"Sala: {reservation.room.name:20s} | "
              f"Fecha: {reservation.start_time.strftime('%Y-%m-%d %H:%M')} | "
              f"Estado: {review_status}")
    
    if len(completed_reservations) > 10:
        print(f"... y {len(completed_reservations) - 10} más")

if __name__ == "__main__":
    print("🎯 Script para Crear Reservas Completadas")
    print("=" * 50)
    
    # Mostrar reservas existentes
    show_existing_completed_reservations()
    
    # Preguntar si crear nuevas reservas
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        create_completed_reservations()
    else:
        print(f"\n💡 Para crear nuevas reservas completadas, ejecuta:")
        print(f"   python create_completed_reservations.py --create")
