"""
Script para crear reservas de ejemplo en el sistema.
Útil para pruebas y demostración.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Añadir el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar modelos
from django.contrib.auth import get_user_model
from rooms.models import Room, Reservation
from django.utils import timezone

User = get_user_model()

def determinar_rol_usuario(usuario):
    """Determina el rol del usuario basándose en su username"""
    username = usuario.username.lower()
    
    if 'admin' in username:
        return 'admin'
    elif 'profesor' in username:
        return 'profesor'
    elif 'soporte' in username:
        return 'soporte'
    else:
        return 'estudiante'

def crear_reservas_ejemplo():
    """Crea reservas de ejemplo para diferentes usuarios y salas"""
    
    print("🎯 Creando reservas de ejemplo...")
    
    # Obtener usuarios y salas existentes
    usuarios = list(User.objects.all())
    salas = list(Room.objects.all())
    
    if not usuarios:
        print("❌ No hay usuarios en la base de datos. Ejecuta setup_users.py primero")
        return
    
    if not salas:
        print("❌ No hay salas en la base de datos. Ejecuta setup_db.py primero")
        return
    
    print(f"📊 Usuarios disponibles: {len(usuarios)}")
    print(f"📊 Salas disponibles: {len(salas)}")
      # Definir algunos horarios típicos
    horarios_comunes = [
        (8, 0, 10, 0),   # 8:00 - 10:00
        (10, 0, 12, 0),  # 10:00 - 12:00
        (12, 0, 14, 0),  # 12:00 - 14:00
        (14, 0, 16, 0),  # 14:00 - 16:00
        (16, 0, 18, 0),  # 16:00 - 18:00
        (18, 0, 20, 0),  # 18:00 - 20:00
    ]
    
    propósitos = [
        "Estudio individual",
        "Reunión de grupo",
        "Preparación de examen",
        "Proyecto de clase",
        "Tutoría",
        "Investigación",
        "Trabajo colaborativo",
        "Práctica de presentación"
    ]
    
    # Notas específicas por tipo de usuario
    notas_por_rol = {
        'estudiante': [
            "Dejar la calefacción encendida, por favor",
            "Necesito acceso a enchufes para portátil",
            "Por favor, mantener silencio en la sala",
            "Solicito que la temperatura esté a 22°C",
            "Necesito buena iluminación para leer",
            "Por favor, limpiar la pizarra antes",
            "Requiero acceso a WiFi estable",
            "Solicito sillas cómodas para estudio prolongado"
        ],
        'profesor': [
            "Necesito un adaptador USB para la clase",
            "Por favor, dejar el proyector encendido",
            "Solicito pizarra limpia antes de la sesión",
            "Requiero micrófono inalámbrico",
            "Necesito acceso a la red del campus",
            "Por favor, verificar funcionamiento del audio",
            "Solicito marcadores de colores nuevos",
            "Requiero control remoto para presentación"
        ],
        'admin': [
            "Revisión de equipamiento técnico",
            "Solicito limpieza especial de la sala",
            "Verificar acceso restringido",
            "Inspección de sistemas de seguridad",
            "Mantenimiento preventivo de equipos",
            "Verificación de protocolos de emergencia",
            "Control de inventario de mobiliario",
            "Supervisión de normativas de seguridad"
        ],
        'soporte': [
            "Mantenimiento técnico programado",
            "Verificación de sistemas informáticos",
            "Actualización de software instalado",
            "Revisión de conectividad de red",
            "Calibración de equipos audiovisuales",
            "Limpieza técnica de computadores",
            "Verificación de licencias de software",
            "Backup de configuraciones del sistema"
        ]
    }
    
    estados = ['confirmed', 'pending', 'completed', 'cancelled']
    
    reservas_creadas = 0
    errores = 0
    
    # Crear reservas para los próximos 30 días
    for dia in range(-7, 23):  # 7 días atrás, 22 días adelante
        fecha = timezone.now().date() + timedelta(days=dia)
        
        # Crear 3-8 reservas por día
        num_reservas_dia = random.randint(3, 8)
        
        for _ in range(num_reservas_dia):
            try:
                # Seleccionar usuario y sala aleatoriamente
                usuario = random.choice(usuarios)
                sala = random.choice(salas)
                
                # Seleccionar horario aleatorio
                hora_inicio, min_inicio, hora_fin, min_fin = random.choice(horarios_comunes)
                
                # Crear datetime objects
                inicio = timezone.make_aware(datetime.combine(
                    fecha, 
                    datetime.min.time().replace(hour=hora_inicio, minute=min_inicio)
                ))
                
                fin = timezone.make_aware(datetime.combine(
                    fecha, 
                    datetime.min.time().replace(hour=hora_fin, minute=min_fin)
                ))
                
                # Verificar que no haya conflictos
                conflictos = Reservation.objects.filter(
                    room=sala,
                    start_time__lt=fin,
                    end_time__gt=inicio,
                    status='confirmed'
                ).exists()
                
                if conflictos:
                    continue  # Saltar si hay conflicto
                  # Determinar estado basado en la fecha
                if fecha < timezone.now().date():
                    # Reservas pasadas: completed o cancelled
                    estado = random.choice(['completed', 'cancelled'])
                elif fecha == timezone.now().date():
                    # Hoy: confirmed, completed o pending
                    estado = random.choice(['confirmed', 'completed', 'pending'])
                else:
                    # Futuras: confirmed o pending
                    estado = random.choice(['confirmed', 'pending'])
                
                # Determinar rol del usuario y seleccionar nota apropiada
                rol_usuario = determinar_rol_usuario(usuario)
                nota_seleccionada = random.choice(notas_por_rol.get(rol_usuario, ["Sin requerimientos especiales"]))
                
                # Crear la reserva
                reserva = Reservation.objects.create(
                    user=usuario,
                    room=sala,
                    start_time=inicio,
                    end_time=fin,
                    purpose=random.choice(propósitos),
                    status=estado,
                    notes=nota_seleccionada
                )
                
                reservas_creadas += 1
                
                if reservas_creadas % 10 == 0:
                    print(f"✅ {reservas_creadas} reservas creadas...")
                
            except Exception as e:
                errores += 1
                if errores < 5:  # Solo mostrar los primeros 5 errores
                    print(f"⚠️ Error creando reserva: {e}")
    
    print(f"\n🎉 ¡Proceso completado!")
    print(f"✅ Reservas creadas: {reservas_creadas}")
    print(f"❌ Errores: {errores}")
    
    # Mostrar estadísticas por estado
    print(f"\n📊 ESTADÍSTICAS POR ESTADO:")
    print("-" * 40)
    for estado, nombre in Reservation.STATUS_CHOICES:
        count = Reservation.objects.filter(status=estado).count()
        print(f"{nombre}: {count}")

def limpiar_reservas():
    """Elimina todas las reservas existentes"""
    count = Reservation.objects.count()
    if count > 0:
        respuesta = input(f"⚠️ ¿Eliminar {count} reservas existentes? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            Reservation.objects.all().delete()
            print(f"🗑️ {count} reservas eliminadas")
        else:
            print("❌ Operación cancelada")
    else:
        print("ℹ️ No hay reservas para eliminar")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        limpiar_reservas()
    else:
        crear_reservas_ejemplo()
