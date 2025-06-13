"""
Script para repoblar SOLO las reservas y reseñas del sistema, manteniendo usuarios y salas.
Útil para refrescar datos para demostraciones.
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
from rooms.models import Room, Reservation, Review
from django.utils import timezone
from django.db import transaction

User = get_user_model()

def limpiar_reservas_y_reseñas():
    """Elimina solo reservas y reseñas, manteniendo usuarios y salas"""
    print("\n🧹 LIMPIANDO RESERVAS Y RESEÑAS...")
    print("-" * 50)
    
    reviews_count = Review.objects.count()
    reservations_count = Reservation.objects.count()
    
    print(f"📊 Datos a eliminar:")
    print(f"   - Reseñas: {reviews_count}")
    print(f"   - Reservas: {reservations_count}")
    
    if reviews_count > 0 or reservations_count > 0:
        respuesta = input(f"⚠️ ¿Confirmar eliminación? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            with transaction.atomic():
                Review.objects.all().delete()
                Reservation.objects.all().delete()
            print("✅ Limpieza completada")
        else:
            print("❌ Operación cancelada")
            return False
    else:
        print("ℹ️ No hay datos para limpiar")
    
    return True

def crear_reservas_actualizadas():
    """Crea reservas con fechas actualizadas"""
    print("\n🎯 CREANDO RESERVAS ACTUALIZADAS...")
    print("-" * 50)
    
    # Obtener usuarios y salas existentes
    usuarios = list(User.objects.all())
    salas = list(Room.objects.all())
    
    if not usuarios:
        print("❌ No hay usuarios en la base de datos")
        return False
    
    if not salas:
        print("❌ No hay salas en la base de datos")
        return False
    
    print(f"📊 Usuarios disponibles: {len(usuarios)}")
    print(f"📊 Salas disponibles: {len(salas)}")
    
    # Horarios típicos para reservas
    horarios_comunes = [
        (8, 0, 10, 0),   # 8:00 - 10:00
        (10, 0, 12, 0),  # 10:00 - 12:00
        (12, 0, 14, 0),  # 12:00 - 14:00
        (14, 0, 16, 0),  # 14:00 - 16:00
        (16, 0, 18, 0),  # 16:00 - 18:00
        (18, 0, 20, 0),  # 18:00 - 20:00
    ]
    
    reservas_creadas = 0
    errores = 0
    
    # Crear reservas: 7 días atrás hasta 30 días adelante
    for dia in range(-7, 31):
        fecha = timezone.now().date() + timedelta(days=dia)
        
        # Más reservas en días laborables
        if fecha.weekday() < 5:  # Lunes a Viernes
            num_reservas_dia = random.randint(4, 8)
        else:  # Fin de semana
            num_reservas_dia = random.randint(2, 5)
        
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
                    end_time__gt=inicio
                ).exists()
                
                if not conflictos:
                    # Determinar estado según la fecha
                    if fecha < timezone.now().date():
                        # Reservas pasadas: completed o cancelled
                        estados_pasados = ['completed', 'cancelled']
                        pesos = [0.8, 0.2]  # 80% completed, 20% cancelled
                        status = random.choices(estados_pasados, weights=pesos)[0]
                    elif fecha == timezone.now().date():
                        # Reservas de hoy: active o completed
                        if inicio < timezone.now():
                            status = 'completed'
                        else:
                            status = 'active'
                    else:
                        # Reservas futuras: active
                        status = 'active'
                    
                    # Crear la reserva
                    reserva = Reservation.objects.create(
                        user=usuario,
                        room=sala,
                        start_time=inicio,
                        end_time=fin,
                        purpose=random.choice([
                            'Reunión de trabajo',
                            'Presentación',
                            'Capacitación',
                            'Videoconferencia',
                            'Estudio grupal',
                            'Taller',
                            'Seminario',
                            'Evaluación'
                        ]),
                        status=status
                    )
                    
                    reservas_creadas += 1
                    
                    if reservas_creadas % 20 == 0:
                        print(f"✅ {reservas_creadas} reservas creadas...")
                        
            except Exception as e:
                errores += 1
                if errores <= 5:  # Solo mostrar los primeros 5 errores
                    print(f"⚠️ Error creando reserva: {e}")
    
    print(f"\n✅ RESERVAS CREADAS: {reservas_creadas}")
    if errores > 0:
        print(f"⚠️ Errores encontrados: {errores}")
    
    return reservas_creadas > 0

def crear_reseñas_actualizadas():
    """Crea reseñas para reservas completadas"""
    print("\n⭐ CREANDO RESEÑAS ACTUALIZADAS...")
    print("-" * 50)
    
    # Obtener reservas completadas sin reseñas
    reservas_completadas = Reservation.objects.filter(
        status='completed'
    ).exclude(
        id__in=Review.objects.values_list('reservation_id', flat=True)
    )
    
    print(f"📊 Reservas completadas sin reseñas: {reservas_completadas.count()}")
    
    reseñas_creadas = 0
    
    # Crear reseñas para aproximadamente el 60% de las reservas completadas
    for reserva in reservas_completadas:
        if random.random() < 0.6:  # 60% de probabilidad
            try:
                rating = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[0.05, 0.1, 0.15, 0.35, 0.35]  # Más ratings altos
                )[0]
                
                comentarios_positivos = [
                    "Excelente sala, muy cómoda y bien equipada.",
                    "Perfecta para reuniones, buena acústica.",
                    "Muy limpia y organizada, recomendada.",
                    "Ideal para presentaciones, proyector funcionó perfecto.",
                    "Ambiente tranquilo, perfecto para concentrarse.",
                    "Buena ubicación y fácil acceso.",
                ]
                
                comentarios_neutros = [
                    "Sala decente, cumple con lo necesario.",
                    "Regular, podría mejorar la iluminación.",
                    "Está bien, aunque un poco pequeña.",
                    "Funcional pero básica.",
                ]
                
                comentarios_negativos = [
                    "Sala muy calurosa, aire acondicionado no funcionaba bien.",
                    "Proyector presentó fallas durante la reunión.",
                    "Un poco ruidosa por estar cerca del pasillo.",
                ]
                
                if rating >= 4:
                    comment = random.choice(comentarios_positivos)
                elif rating == 3:
                    comment = random.choice(comentarios_neutros)
                else:
                    comment = random.choice(comentarios_negativos)                
                    Review.objects.create(
                    reservation=reserva,
                    rating=rating,
                    comment=comment
                )
                
                reseñas_creadas += 1
                
            except Exception as e:
                print(f"⚠️ Error creando reseña: {e}")
    
    print(f"✅ RESEÑAS CREADAS: {reseñas_creadas}")
    
    return reseñas_creadas > 0

def mostrar_estadisticas():
    """Muestra estadísticas finales"""
    print("\n📊 ESTADÍSTICAS FINALES:")
    print("=" * 50)
    
    total_users = User.objects.count()
    total_rooms = Room.objects.count()
    total_reservations = Reservation.objects.count()
    total_reviews = Review.objects.count()
    
    print(f"👥 Usuarios: {total_users}")
    print(f"🏢 Salas: {total_rooms}")
    print(f"📅 Reservas: {total_reservations}")
    print(f"⭐ Reseñas: {total_reviews}")
    
    # Estadísticas por estado de reserva
    for status in ['active', 'completed', 'cancelled']:
        count = Reservation.objects.filter(status=status).count()
        print(f"   - {status.title()}: {count}")

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("=== REPOBLADO DE RESERVAS Y RESEÑAS ===")
    print("="*80)
    print("Este script actualiza solo reservas y reseñas, manteniendo usuarios y salas")
    
    # Paso 1: Limpiar datos existentes
    if not limpiar_reservas_y_reseñas():
        return
    
    # Paso 2: Crear nuevas reservas
    if not crear_reservas_actualizadas():
        print("❌ Error creando reservas")
        return
    
    # Paso 3: Crear nuevas reseñas
    crear_reseñas_actualizadas()
    
    # Paso 4: Mostrar estadísticas
    mostrar_estadisticas()
    
    print("\n🎉 ¡REPOBLADO COMPLETADO EXITOSAMENTE!")
    print("Los datos están listos para la demostración.")

if __name__ == "__main__":
    main()
