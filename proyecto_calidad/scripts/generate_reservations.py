"""
Script para generar reservas aleatorias en el sistema.

Este script crea reservaciones aleatorias utilizando los usuarios y salas
ya existentes en la base de datos, respetando los permisos por rol.

Se debe ejecutar con: python manage.py shell < generate_reservations.py
"""

import os
import django
import random
from datetime import datetime, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
from django.utils import timezone
from rooms.models import Room, Reservation

User = get_user_model()

# Propósitos comunes para reservas
PROPOSITOS = [
    'Estudio individual',
    'Estudio grupal',
    'Reunión de proyecto',
    'Reunión de equipo docente',
    'Clase particular',
    'Tutoría',
    'Trabajo en grupo',
    'Videoconferencia',
    'Práctica de laboratorio',
    'Preparación de examen',
    'Presentación de proyecto',
    'Investigación',
    'Lectura y documentación',
    'Entrevista',
    'Sesión de estudio',
]

def generar_fecha_aleatoria(dias_futuro_max=30):
    """Genera una fecha aleatoria entre hoy y X días en el futuro"""
    hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dias_aleatorios = random.randint(1, dias_futuro_max)
    fecha_base = hoy + timedelta(days=dias_aleatorios)
    
    # Asegurar que la hora esté dentro del horario habitual (8-22)
    hora = random.randint(8, 21)
    minutos = random.choice([0, 15, 30, 45])
    
    return fecha_base.replace(hour=hora, minute=minutos)

def crear_reservas(cantidad=50):
    """Crea reservas aleatorias respetando permisos por rol"""
    
    reservas_creadas = []
    print(f"Generando {cantidad} reservas aleatorias...")
    
    # Obtener todas las salas activas
    salas = list(Room.objects.filter(is_active=True))
    if not salas:
        print("No hay salas disponibles para reservar.")
        return []
    
    # Obtener usuarios por rol
    profesores = list(User.objects.filter(role='profesor'))
    estudiantes = list(User.objects.filter(role='estudiante'))
    soporte = list(User.objects.filter(role='soporte'))
    admins = list(User.objects.filter(role='admin'))
    
    # Combinar todos los usuarios
    todos_usuarios = profesores + estudiantes + soporte + admins
    
    intentos = 0
    while len(reservas_creadas) < cantidad and intentos < cantidad * 3:
        intentos += 1
        
        # Seleccionar usuario aleatorio
        usuario = random.choice(todos_usuarios)
        
        # Filtrar salas que el usuario puede reservar
        salas_disponibles = [sala for sala in salas if sala.can_be_reserved_by(usuario)]
        
        if not salas_disponibles:
            print(f"No hay salas disponibles para el usuario {usuario.username} con rol {usuario.role}")
            continue
        
        sala = random.choice(salas_disponibles)
        
        # Generar fecha y hora de inicio aleatorias
        fecha_inicio = generar_fecha_aleatoria()
        
        # Duración aleatoria entre 1 y 3 horas
        duracion_horas = random.randint(1, 3)
        fecha_fin = fecha_inicio + timedelta(hours=duracion_horas)
        
        # Verificar si la sala está disponible en ese horario
        if not sala.is_available_at(fecha_inicio, fecha_fin):
            continue
        
        # Generar propósito aleatorio
        proposito = random.choice(PROPOSITOS)
        
        # Generar número de asistentes aleatorio (no más que la capacidad)
        asistentes = random.randint(1, min(10, sala.capacity))
        
        # Estado aleatorio, con mayor probabilidad para 'confirmed'
        estados = ['pending', 'confirmed', 'completed', 'cancelled']
        pesos = [0.1, 0.6, 0.2, 0.1]
        estado = random.choices(estados, weights=pesos)[0]
        
        # Si la fecha es pasada, marcar como completada
        if fecha_inicio < timezone.now():
            estado = 'completed'
        
        try:
            reserva = Reservation.objects.create(
                room=sala,
                user=usuario,
                start_time=fecha_inicio,
                end_time=fecha_fin,
                purpose=proposito,
                status=estado,
                attendees_count=asistentes,
                notes=f"Reserva generada automáticamente para {proposito}"
            )
            
            reservas_creadas.append(reserva)
            print(f"Reserva creada: {sala.name} - {usuario.username} - {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
        except Exception as e:
            print(f"Error al crear reserva: {e}")
    
    return reservas_creadas

def crear_reservas_por_tipo_usuario(num_por_tipo=5):
    """Crea un número específico de reservas para cada tipo de usuario"""
    
    reservas = []
    
    # Crear reservas para profesores
    profesores = list(User.objects.filter(role='profesor')[:5])
    for profesor in profesores:
        # Los profesores pueden reservar cualquier tipo de sala
        salas = list(Room.objects.filter(is_active=True).order_by('?')[:num_por_tipo])
        for sala in salas:
            try:
                fecha_inicio = generar_fecha_aleatoria()
                fecha_fin = fecha_inicio + timedelta(hours=2)
                
                if sala.is_available_at(fecha_inicio, fecha_fin):
                    reserva = Reservation.objects.create(
                        room=sala,
                        user=profesor,
                        start_time=fecha_inicio,
                        end_time=fecha_fin,
                        purpose=f"Reserva de profesor en {sala.room_type}",
                        status='confirmed',
                        attendees_count=random.randint(1, min(10, sala.capacity))
                    )
                    reservas.append(reserva)
                    print(f"Reserva de profesor: {profesor.username} - {sala.name}")
            except Exception as e:
                print(f"Error en reserva de profesor: {e}")
    
    # Crear reservas para estudiantes (solo salas de estudio y salas individuales)
    estudiantes = list(User.objects.filter(role='estudiante')[:5])
    salas_estudiantes = list(Room.objects.filter(
        is_active=True, 
        room_type__in=['sala_estudio', 'sala_individual']
    ).order_by('?'))
    
    for estudiante in estudiantes:
        # Seleccionar algunas salas aleatorias que los estudiantes pueden reservar
        salas_seleccionadas = salas_estudiantes[:num_por_tipo]
        for sala in salas_seleccionadas:
            try:
                fecha_inicio = generar_fecha_aleatoria()
                fecha_fin = fecha_inicio + timedelta(hours=2)
                
                if sala.is_available_at(fecha_inicio, fecha_fin):
                    reserva = Reservation.objects.create(
                        room=sala,
                        user=estudiante,
                        start_time=fecha_inicio,
                        end_time=fecha_fin,
                        purpose=f"Estudio en {sala.name}",
                        status='confirmed',
                        attendees_count=random.randint(1, min(4, sala.capacity))
                    )
                    reservas.append(reserva)
                    print(f"Reserva de estudiante: {estudiante.username} - {sala.name}")
            except Exception as e:
                print(f"Error en reserva de estudiante: {e}")
                
    # Crear reservas para soporte técnico (principalmente salas de reuniones)
    soporte = list(User.objects.filter(role='soporte')[:3])
    salas_soporte = list(Room.objects.filter(
        is_active=True, 
        room_type__in=['sala_reunion']
    ).order_by('?'))
    
    for tecnico in soporte:
        salas_seleccionadas = salas_soporte[:num_por_tipo]
        for sala in salas_seleccionadas:
            try:
                fecha_inicio = generar_fecha_aleatoria()
                fecha_fin = fecha_inicio + timedelta(hours=1)
                
                if sala.is_available_at(fecha_inicio, fecha_fin):
                    reserva = Reservation.objects.create(
                        room=sala,
                        user=tecnico,
                        start_time=fecha_inicio,
                        end_time=fecha_fin,
                        purpose="Reunión de soporte técnico",
                        status='confirmed',
                        attendees_count=random.randint(2, min(6, sala.capacity))
                    )
                    reservas.append(reserva)
                    print(f"Reserva de soporte: {tecnico.username} - {sala.name}")
            except Exception as e:
                print(f"Error en reserva de soporte: {e}")
    
    return reservas

if __name__ == '__main__':
    # Verificar si ya existen suficientes reservas
    if Reservation.objects.count() > 20:
        print(f"Ya hay {Reservation.objects.count()} reservas en la base de datos.")
        respuesta = input("¿Desea crear más reservas? (s/n): ")
        if respuesta.lower() != 's':
            print("Operación cancelada.")
            exit()
    
    # Crear reservas por tipo de usuario
    print("\nCreando reservas específicas por tipo de usuario...")
    reservas_especificas = crear_reservas_por_tipo_usuario(3)
    
    # Crear reservas aleatorias adicionales
    print("\nCreando reservas aleatorias generales...")
    reservas_aleatorias = crear_reservas(30)
    
    # Mostrar resumen
    print("\nResumen de reservas creadas:")
    print(f"- Reservas específicas por tipo de usuario: {len(reservas_especificas)}")
    print(f"- Reservas aleatorias generales: {len(reservas_aleatorias)}")
    print(f"- Total nuevas reservas: {len(reservas_especificas) + len(reservas_aleatorias)}")
    print(f"- Total reservas en sistema: {Reservation.objects.count()}")
    
    # Estadísticas por estado
    print("\nReservas por estado:")
    for estado, nombre in Reservation.STATUS_CHOICES:
        count = Reservation.objects.filter(status=estado).count()
        print(f"- {nombre}: {count}")
    
    # Estadísticas por tipo de sala
    print("\nReservas por tipo de sala:")
    for tipo, _ in Room.ROOM_TYPE_CHOICES:
        count = Reservation.objects.filter(room__room_type=tipo).count()
        print(f"- {tipo}: {count}")
    
    # Estadísticas por rol de usuario
    print("\nReservas por rol de usuario:")
    for rol, _ in User.ROLE_CHOICES:
        count = Reservation.objects.filter(user__role=rol).count()
        print(f"- {rol}: {count}")
