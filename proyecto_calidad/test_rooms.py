#!/usr/bin/env python
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from rooms.models import Room

# Verificar salas existentes
rooms = Room.objects.all()
print(f"Total de salas: {rooms.count()}")

if rooms.count() > 0:
    print("\nPrimeras 5 salas:")
    for r in rooms[:5]:
        print(f"- {r.name}")
        print(f"  Tipo: {r.room_type}")
        print(f"  Precio: ${r.hourly_rate}")
        print(f"  Capacidad: {r.capacity}")
        print()
else:
    print("No hay salas en la base de datos")
