#!/usr/bin/env python
"""
Script para verificar las configuraciones de zona horaria y tiempo
en el sistema de gestión de salas.

Compara:
- Hora del sistema local
- Hora de Django (UTC y zona horaria configurada)
- Zona horaria de Chile
- Horarios de las salas en la base de datos
"""

import os
import sys
import django
from datetime import datetime, timezone as dt_timezone
import pytz

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
from rooms.models import Room, Reservation


def main():
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIONES DE TIEMPO")
    print("=" * 60)
    
    # 1. Hora del sistema local
    print("\n1. HORA DEL SISTEMA LOCAL:")
    local_now = datetime.now()
    print(f"   Hora local (naive):     {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Zona horaria sistema:   {local_now.astimezone().tzinfo}")
    
    # 2. Configuración de Django
    print("\n2. CONFIGURACIÓN DE DJANGO:")
    print(f"   TIME_ZONE setting:      {settings.TIME_ZONE}")
    print(f"   USE_TZ setting:         {settings.USE_TZ}")
    
    # 3. Hora de Django
    print("\n3. HORA DE DJANGO:")
    django_now_utc = timezone.now()
    print(f"   Django UTC:             {django_now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 4. Zona horaria de Chile
    print("\n4. ZONA HORARIA DE CHILE:")
    chile_tz = pytz.timezone('America/Santiago')
    chile_now = django_now_utc.astimezone(chile_tz)
    print(f"   Hora Chile:             {chile_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Offset UTC:             {chile_now.strftime('%z')}")
    
    # 5. Verificar si Chile está en horario de verano
    is_dst = chile_now.dst().total_seconds() != 0
    print(f"   Horario de verano:      {'Sí' if is_dst else 'No'}")
    
    # 6. Diferencias de tiempo
    print("\n5. DIFERENCIAS DE TIEMPO:")
    local_aware = local_now.replace(tzinfo=dt_timezone.utc)
    diff_django_local = (django_now_utc - local_aware).total_seconds()
    diff_chile_local = (chile_now.replace(tzinfo=None) - local_now).total_seconds()
    
    print(f"   Django UTC vs Local:    {diff_django_local/3600:.1f} horas")
    print(f"   Chile vs Local:         {diff_chile_local/3600:.1f} horas")
    
    # 7. Verificar salas en la base de datos
    print("\n6. VERIFICACIÓN DE SALAS:")
    try:
        rooms = Room.objects.filter(is_active=True)[:3]  # Solo las primeras 3 salas
        
        for room in rooms:
            print(f"\n   Sala: {room.name}")
            print(f"   - Horario apertura:     {room.opening_time}")
            print(f"   - Horario cierre:       {room.closing_time}")
            print(f"   - ¿Abierta ahora?:      {'Sí' if room.is_open_now else 'No'}")
            print(f"   - ¿Disponible ahora?:   {'Sí' if room.is_available_now else 'No'}")
            
            # Obtener estado detallado
            status = room.get_detailed_availability_status()
            print(f"   - Estado detallado:     {status['message']}")
            
    except Exception as e:
        print(f"   Error accediendo a salas: {e}")
    
    # 8. Verificar reservas recientes
    print("\n7. RESERVAS RECIENTES:")
    try:
        recent_reservations = Reservation.objects.filter(
            start_time__gte=django_now_utc - timezone.timedelta(hours=24)
        ).order_by('-created_at')[:3]
        
        if recent_reservations.exists():
            for reservation in recent_reservations:
                print(f"\n   Reserva: {reservation.room.name}")
                print(f"   - Usuario:              {reservation.user.username}")
                print(f"   - Inicio (UTC):         {reservation.start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   - Inicio (Chile):       {reservation.start_time.astimezone(chile_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   - Fin (UTC):            {reservation.end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   - Fin (Chile):          {reservation.end_time.astimezone(chile_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   - Estado:               {reservation.status}")
                print(f"   - ¿Activa?:             {'Sí' if reservation.is_active else 'No'}")
        else:
            print("   No hay reservas recientes en las últimas 24 horas")
            
    except Exception as e:
        print(f"   Error accediendo a reservas: {e}")
    
    # 9. Pruebas de conversión de tiempo
    print("\n8. PRUEBAS DE CONVERSIÓN:")
    
    # Crear una fecha de prueba en Chile
    test_date_chile = chile_tz.localize(datetime(2025, 6, 13, 14, 30, 0))
    test_date_utc = test_date_chile.astimezone(pytz.UTC)
    
    print(f"   Fecha prueba Chile:     {test_date_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Misma fecha en UTC:     {test_date_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Diferencia:             {(test_date_chile.utcoffset().total_seconds()/3600):.0f} horas")
    
    # 10. Recomendaciones
    print("\n9. RECOMENDACIONES:")
    
    if abs(diff_chile_local) > 3600:  # Más de 1 hora de diferencia
        print("   ⚠️  ADVERTENCIA: Hay más de 1 hora de diferencia entre hora local y Chile")
        print("      Esto puede causar problemas en las reservas")
    
    if not settings.USE_TZ:
        print("   ⚠️  ADVERTENCIA: USE_TZ está deshabilitado en Django")
        print("      Se recomienda habilitarlo para manejo correcto de zonas horarias")
    
    if settings.TIME_ZONE != 'America/Santiago':
        print(f"   ⚠️  ADVERTENCIA: TIME_ZONE está configurado como {settings.TIME_ZONE}")
        print("      Para una aplicación en Chile, se recomienda 'America/Santiago'")
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    main()
