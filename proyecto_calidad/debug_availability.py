#!/usr/bin/env python
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from rooms.models import Room
from django.utils import timezone
from datetime import time

# Verificar una sala específica
rooms = Room.objects.all()[:5]
now = timezone.now()

print(f"=== DIAGNÓSTICO DE DISPONIBILIDAD ===")
print(f"Hora actual: {now.time()}")
print(f"Fecha actual: {now.date()}")
print()

for room in rooms:
    print(f"SALA: {room.name}")
    print(f"  Horario: {room.opening_time} - {room.closing_time}")
    
    # Verificar horario
    within_hours = room.opening_time <= now.time() <= room.closing_time
    print(f"  Dentro de horario: {within_hours}")
    
    # Verificar reservas activas
    active_reservations = room.reservations.filter(
        status__in=['confirmed', 'in_progress'],
        start_time__lte=now,
        end_time__gt=now
    )
    
    print(f"  Reservas activas: {active_reservations.count()}")
    for res in active_reservations:
        print(f"    - {res.start_time} a {res.end_time} (Usuario: {res.user.username})")
    
    print(f"  ¿Disponible ahora? {room.is_available_now}")
    print("-" * 50)
