#!/usr/bin/env python
"""
Script para poblar más reseñas en el sistema.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from rooms.models import Room, Reservation, Review
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

def poblar_reseñas():
    """Pobla más reseñas en el sistema."""
    print("🔄 Poblando más reseñas...")
    
    # Verificar estado actual
    reservas_totales = Reservation.objects.all().count()
    reseñas_existentes = Review.objects.all().count()
    
    print(f"📊 Estado actual:")
    print(f"   - Total reservas: {reservas_totales}")
    print(f"   - Total reseñas: {reseñas_existentes}")
    
    # Obtener reservas pasadas que podrían estar completadas
    now = timezone.now()
    reservas_pasadas = Reservation.objects.filter(
        end_time__lt=now,
        status__in=['confirmed', 'in_progress']
    )[:20]  # Tomar las primeras 20
    
    print(f"   - Reservas pasadas que pueden completarse: {reservas_pasadas.count()}")
    
    # Completar las reservas pasadas
    for reserva in reservas_pasadas:
        reserva.status = 'completed'
        reserva.save()
    
    print(f"✅ Se marcaron {reservas_pasadas.count()} reservas como completadas")
    
    # Obtener reservas completadas sin reseñas
    reservas_sin_reseña = Reservation.objects.filter(
        status='completed'
    ).exclude(review__isnull=False)[:15]  # Crear reseñas para las primeras 15
    
    print(f"📝 Creando reseñas para {reservas_sin_reseña.count()} reservas...")
    
    # Comentarios de ejemplo por rating
    comentarios_por_rating = {
        5: [
            "Excelente sala, muy limpia y con buen equipamiento.",
            "Perfecta para estudiar, ambiente muy tranquilo.",
            "Todo funcionó perfecto, la recomiendo totalmente.",
            "Instalaciones impecables y muy cómodas.",
            "La mejor sala que he usado, 10/10.",
            "Perfecta ubicación y excelente mantenimiento.",
            "Superó mis expectativas, volveré sin dudas."
        ],
        4: [
            "Muy buena sala, solo le falta un poco más de iluminación.",
            "Excelente en general, pequeños detalles por mejorar.",
            "Muy cómoda y funcional, casi perfecta.",
            "Buena experiencia, equipamiento en buen estado.",
            "Recomendable, ambiente agradable para estudiar.",
            "Muy satisfecho con la reserva, volvería.",
            "Buena calidad, solo algunos ruidos del exterior."
        ],
        3: [
            "Sala correcta, cumple su función básica.",
            "Está bien, pero podría mejorarse la limpieza.",
            "Funcional pero nada excepcional.",
            "Aceptable para el uso que le di.",
            "Regular, hay salas mejores disponibles.",
            "Cumple lo mínimo necesario.",
            "No está mal, pero esperaba algo mejor."
        ],
        2: [
            "Un poco ruidosa por estar cerca del pasillo.",
            "Equipamiento algo desactualizado.",
            "Necesita mejor mantenimiento.",
            "La limpieza podría mejorar considerablemente.",
            "Varias cosas no funcionaban correctamente.",
            "Decepcionante comparado con otras salas.",
            "Muchas distracciones por el ruido externo."
        ],
        1: [
            "Muy decepcionante, equipamiento en mal estado.",
            "Demasiado ruidosa, imposible concentrarse.",
            "Pésimas condiciones de limpieza.",
            "No recomiendo esta sala para nada.",
            "Experiencia muy negativa, buscaré otras opciones.",
            "Completamente insatisfecho con el servicio.",
            "Condiciones inaceptables para estudiar."
        ]
    }
    
    tipos_comentario_por_rating = {
        5: 'positive',
        4: 'positive', 
        3: 'neutral',
        2: 'suggestion',
        1: 'problem'
    }
    
    reseñas_creadas = 0
    
    for reserva in reservas_sin_reseña:
        try:
            # Generar calificación con distribución realista (más 4s y 5s)
            rating_weights = [1, 2, 3, 6, 8]  # Más probabilidad de ratings altos
            rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
            
            # Seleccionar comentario apropiado
            comentario = random.choice(comentarios_por_rating[rating])
            tipo_comentario = tipos_comentario_por_rating[rating]
            
            # Generar calificaciones específicas (pueden variar ±1 del rating general)
            cleanliness = max(1, min(5, rating + random.randint(-1, 1)))
            equipment = max(1, min(5, rating + random.randint(-1, 1)))
            comfort = max(1, min(5, rating + random.randint(-1, 1)))
            
            # Crear la reseña
            review = Review.objects.create(
                reservation=reserva,
                rating=rating,
                cleanliness_rating=cleanliness,
                equipment_rating=equipment,
                comfort_rating=comfort,
                comment=comentario,
                comment_type=tipo_comentario
            )
            
            reseñas_creadas += 1
            print(f"   ✅ Reseña creada: {reserva.room.name} - {rating}★ por {reserva.user.username}")
            
        except Exception as e:
            print(f"   ❌ Error creando reseña para reserva {reserva.id}: {e}")
    
    print(f"\n🎉 Proceso completado:")
    print(f"   - Reseñas creadas: {reseñas_creadas}")
    print(f"   - Total reseñas ahora: {Review.objects.count()}")
    
    # Mostrar estadísticas por sala
    print(f"\n📊 Estadísticas por sala:")
    for room in Room.objects.all()[:10]:  # Mostrar solo las primeras 10
        total_reviews = Review.objects.filter(reservation__room=room).count()
        if total_reviews > 0:
            avg_rating = Review.objects.filter(reservation__room=room).aggregate(
                avg=models.Avg('rating')
            )['avg']
            print(f"   - {room.name}: {total_reviews} reseñas, promedio {avg_rating:.1f}★")

if __name__ == "__main__":
    from django.db import models
    poblar_reseñas()
