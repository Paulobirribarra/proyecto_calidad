#!/usr/bin/env python
"""
Script para simular el proceso de reserva y debuggear problemas.

Este script simula el envío del formulario de reserva para identificar
dónde está fallando el proceso cuando el botón no responde.
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
from rooms.forms import ReservationForm
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

User = get_user_model()

def simulate_reservation():
    """Simula el proceso completo de reserva."""
    
    print("=" * 60)
    print("🧪 SIMULACIÓN DE RESERVA - DEBUG")
    print("=" * 60)
    
    # 1. Verificar usuarios disponibles
    print("\n1️⃣ Verificando usuarios disponibles...")
    users = User.objects.all()[:5]
    for user in users:
        print(f"   👤 {user.username} - Email: {user.email}")
    
    if not users:
        print("❌ No hay usuarios en la base de datos")
        return
    
    # 2. Verificar salas disponibles
    print("\n2️⃣ Verificando salas disponibles...")
    rooms = Room.objects.filter(is_active=True)[:5]
    for room in rooms:
        print(f"   🏢 {room.name} - Capacidad: {room.capacity} - €{room.hourly_rate}/h")
    
    if not rooms:
        print("❌ No hay salas activas en la base de datos")
        return
    
    # 3. Seleccionar usuario y sala para la prueba
    test_user = users.first()
    test_room = rooms.first()
    
    print(f"\n3️⃣ Usando para la prueba:")
    print(f"   👤 Usuario: {test_user.username}")
    print(f"   🏢 Sala: {test_room.name}")
      # 4. Preparar datos del formulario
    now = timezone.now()
    start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    form_data = {
        'room': test_room.id,  # Incluir el ID de la sala
        'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
        'end_time': end_time.strftime('%Y-%m-%d %H:%M'),
        'attendees_count': 3,
        'purpose': 'Reunión de trabajo - Prueba automatizada'
    }
    
    print(f"\n4️⃣ Datos del formulario:")
    for key, value in form_data.items():
        print(f"   📝 {key}: {value}")
    
    # 5. Probar la validación del formulario
    print(f"\n5️⃣ Probando validación del formulario...")
    
    try:
        form = ReservationForm(data=form_data, user=test_user)
        form.instance.room = test_room
        
        print(f"   ✅ Formulario creado correctamente")
        print(f"   🔍 Datos del formulario: {form.data}")
        
        if form.is_valid():
            print(f"   ✅ Formulario es válido")
            print(f"   📋 Datos limpios: {form.cleaned_data}")
        else:
            print(f"   ❌ Formulario NO es válido")
            print(f"   🚨 Errores: {form.errors}")
            return
        
    except Exception as e:
        print(f"   ❌ Error al crear formulario: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 6. Simular la creación de la reserva
    print(f"\n6️⃣ Simulando creación de reserva...")
    
    try:
        # Verificar disponibilidad
        is_available = test_room.is_available_at(start_time, end_time)
        print(f"   🔍 Sala disponible: {is_available}")
        
        if not is_available:
            conflicts = test_room.reservations.filter(
                status__in=['confirmed', 'in_progress'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            print(f"   ⚠️  Conflictos encontrados:")
            for conflict in conflicts:
                print(f"      - {conflict.start_time} - {conflict.end_time} por {conflict.user.username}")
        
        # Crear la reserva
        reservation = form.save(commit=False)
        reservation.user = test_user
        reservation.room = test_room
        reservation.status = 'confirmed'
        reservation.save()
        
        print(f"   ✅ Reserva creada exitosamente!")
        print(f"   🎫 ID de reserva: {reservation.id}")
        print(f"   📅 Horario: {reservation.start_time} - {reservation.end_time}")
        print(f"   👥 Asistentes: {reservation.attendees_count}")
        print(f"   📝 Propósito: {reservation.purpose}")
        
    except Exception as e:
        print(f"   ❌ Error al crear reserva: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 7. Verificar la reserva en la base de datos
    print(f"\n7️⃣ Verificando reserva en la base de datos...")
    
    try:
        saved_reservation = Reservation.objects.get(id=reservation.id)
        print(f"   ✅ Reserva encontrada en DB")
        print(f"   📊 Estado: {saved_reservation.get_status_display()}")
        print(f"   🏢 Sala: {saved_reservation.room.name}")
        print(f"   👤 Usuario: {saved_reservation.user.username}")
        
    except Exception as e:
        print(f"   ❌ Error al verificar reserva: {str(e)}")
    
    # 8. Probar la vista de reserva simulada
    print(f"\n8️⃣ Simulando petición HTTP POST...")
    
    try:
        factory = RequestFactory()
        request = factory.post(f'/salas/sala/{test_room.id}/reservar/', data=form_data)
        request.user = test_user
        
        # Agregar sesión y mensajes
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        msg_middleware = MessageMiddleware(lambda req: None)
        msg_middleware.process_request(request)
        
        print(f"   ✅ Request HTTP creada")
        print(f"   🌐 Método: {request.method}")
        print(f"   📝 Datos POST: {request.POST}")
        print(f"   👤 Usuario: {request.user.username}")
        
    except Exception as e:
        print(f"   ❌ Error al simular HTTP request: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print("✅ SIMULACIÓN COMPLETADA")
    print("=" * 60)
    
    return reservation

def debug_form_fields():
    """Debuggea los campos del formulario para identificar problemas."""
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG DE CAMPOS DEL FORMULARIO")
    print("=" * 60)
    
    try:
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios para el test")
            return
        
        form = ReservationForm(user=user)
        
        print(f"\n📋 Campos disponibles en el formulario:")
        for field_name, field in form.fields.items():
            print(f"   🔸 {field_name}: {type(field).__name__}")
            print(f"      - Requerido: {field.required}")
            print(f"      - Widget: {type(field.widget).__name__}")
            if hasattr(field.widget, 'attrs'):
                print(f"      - Atributos: {field.widget.attrs}")
        
        print(f"\n🎨 HTML del formulario:")
        print(str(form))
        
    except Exception as e:
        print(f"❌ Error al debuggear formulario: {str(e)}")
        import traceback
        traceback.print_exc()

def check_existing_reservations():
    """Verifica las reservas existentes en la base de datos."""
    
    print("\n" + "=" * 60)
    print("📊 RESERVAS EXISTENTES EN LA BASE DE DATOS")
    print("=" * 60)
    
    reservations = Reservation.objects.all().order_by('-created_at')[:10]
    
    if not reservations:
        print("ℹ️  No hay reservas en la base de datos")
        return
    
    for reservation in reservations:
        print(f"\n🎫 Reserva #{reservation.id}")
        print(f"   👤 Usuario: {reservation.user.username}")
        print(f"   🏢 Sala: {reservation.room.name}")
        print(f"   📅 Inicio: {reservation.start_time}")
        print(f"   🏁 Fin: {reservation.end_time}")
        print(f"   📊 Estado: {reservation.get_status_display()}")
        print(f"   👥 Asistentes: {reservation.attendees_count}")
        print(f"   📝 Propósito: {reservation.purpose[:50]}...")

if __name__ == "__main__":
    print("🚀 Iniciando script de simulación de reservas...")
    
    # Ejecutar todas las pruebas
    check_existing_reservations()
    debug_form_fields()
    
    print("\n" + "=" * 60)
    print("¿Proceder con la simulación de nueva reserva? (y/n): ", end="")
    response = input()
    
    if response.lower() in ['y', 'yes', 's', 'si', 'sí']:
        simulate_reservation()
    else:
        print("⏹️  Simulación cancelada por el usuario")
