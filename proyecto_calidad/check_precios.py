#!/usr/bin/env python
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from rooms.models import Room

# Verificar salas por tipo y precio
tipos_especiales = ['sala_estudio', 'sala_individual']

print("SALAS GRATUITAS (para estudiantes):")
for tipo in tipos_especiales:
    salas = Room.objects.filter(room_type=tipo)
    print(f"\n{tipo.upper()}:")
    for sala in salas:
        precio_texto = "GRATUITA" if sala.hourly_rate == 0 else f"${sala.hourly_rate:,}"
        print(f"  - {sala.name}: {precio_texto}")

print("\n" + "="*50)        
print("SALAS DE PAGO:")
salas_pagas = Room.objects.filter(hourly_rate__gt=0)
for sala in salas_pagas[:5]:  # Solo las primeras 5
    print(f"  - {sala.name} ({sala.room_type}): ${sala.hourly_rate:,}")
    
print(f"\nTotal salas gratuitas: {Room.objects.filter(hourly_rate=0).count()}")
print(f"Total salas de pago: {Room.objects.filter(hourly_rate__gt=0).count()}")
