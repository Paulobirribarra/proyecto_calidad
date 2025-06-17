from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import Room, Reservation, Review
from django.utils import timezone
from django.db import models
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea reseñas de ejemplo para las salas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=15,
            help='Cantidad de reseñas a crear (default: 15)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina reseñas existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        self.stdout.write("🏫 Creando reseñas de ejemplo para Colegio Clara Brincefield...")
        
        if options['reset']:
            reseñas_existentes = Review.objects.count()
            if reseñas_existentes > 0:
                Review.objects.all().delete()
                self.stdout.write(f"🗑️ Eliminadas {reseñas_existentes} reseñas existentes")
        
        # Obtener reservas que pueden tener reseñas
        now = timezone.now()
        reservas_pasadas = Reservation.objects.filter(
            end_time__lt=now
        )
        
        if not reservas_pasadas.exists():
            # Si no hay reservas pasadas, crear algunas en el pasado
            self.stdout.write("📅 Creando reservas pasadas para poder generar reseñas...")
            self._crear_reservas_pasadas()
            reservas_pasadas = Reservation.objects.filter(end_time__lt=now)
        
        # Completar reservas pasadas
        for reserva in reservas_pasadas:
            if reserva.status != 'completed':
                reserva.status = 'completed'
                reserva.save()
        
        # Obtener reservas completadas sin reseñas
        reservas_sin_reseña = reservas_pasadas.filter(
            review__isnull=True
        )[:options['cantidad']]
        
        reseñas_creadas = 0
        comentarios_positivos = [
            "Excelente sala, muy bien equipada y cómoda.",
            "Perfecta para nuestras actividades académicas.",
            "Tecnología moderna y ambiente propicio para el aprendizaje.",
            "Muy satisfecho con las instalaciones del colegio.",
            "Ideal para clases interactivas y dinámicas.",
            "Espacio amplio y bien iluminado.",
            "Equipamiento de primera calidad.",
            "Ambiente muy profesional y ordenado.",
        ]
        
        comentarios_neutrales = [
            "Sala funcional, cumple con lo necesario.",
            "Buen espacio para actividades educativas.",
            "Instalaciones adecuadas para el propósito.",
            "Sala estándar del colegio, sin inconvenientes.",
            "Apropiada para las actividades programadas.",
        ]
        
        comentarios_criticos = [
            "Podría mejorar la ventilación del espacio.",
            "Algunos equipos necesitan mantenimiento.",
            "La temperatura no siempre es la ideal.",
            "Sería bueno actualizar algunos elementos.",        ]
        
        for reserva in reservas_sin_reseña:
            try:
                # Determinar rating basado en probabilidades realistas
                probabilidad = random.random()
                if probabilidad < 0.6:  # 60% ratings altos (4-5)
                    rating = random.choice([4, 5])
                    comentarios = comentarios_positivos
                elif probabilidad < 0.85:  # 25% ratings medios (3)
                    rating = 3
                    comentarios = comentarios_neutrales
                else:  # 15% ratings bajos (1-2)
                    rating = random.choice([1, 2])
                    comentarios = comentarios_criticos
                
                review = Review.objects.create(
                    reservation=reserva,
                    rating=rating,
                    comment=random.choice(comentarios),
                    created_at=reserva.end_time + timedelta(hours=random.randint(1, 48))
                )
                
                reseñas_creadas += 1
                self.stdout.write(f"   ✅ Reseña {reseñas_creadas}: {reserva.user.username} - {reserva.room.name}")
                self.stdout.write(f"      ⭐ Rating: {rating}/5 - '{review.comment[:50]}...'")
                
            except Exception as e:
                self.stdout.write(f"   ⚠️ Error creando reseña: {e}")
                continue
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"✅ RESEÑAS CREADAS: {reseñas_creadas}")
        self.stdout.write("="*50)
        
        # Mostrar estadísticas
        self.stdout.write("\n📊 ESTADÍSTICAS DE RESEÑAS:")
        total_reviews = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg=models.Avg('rating'))['avg'] or 0
        self.stdout.write(f"   Total reseñas: {total_reviews}")
        self.stdout.write(f"   Rating promedio: {avg_rating:.1f}/5")
        
        # Estadísticas por rating
        for rating in [1, 2, 3, 4, 5]:
            count = Review.objects.filter(rating=rating).count()
            self.stdout.write(f"   {rating} estrellas: {count} reseñas")

    def _crear_reservas_pasadas(self):
        """Crea algunas reservas en el pasado para poder generar reseñas"""
        usuarios = list(User.objects.all())
        salas = list(Room.objects.all())
        
        if not usuarios or not salas:
            return
        
        now = timezone.now()
        
        for i in range(10):
            try:
                usuario = random.choice(usuarios)
                sala = random.choice(salas)
                
                # Crear reserva de hace 1-7 días
                dias_atras = random.randint(1, 7)
                hora_inicio = random.randint(8, 16)
                
                start_time = now - timedelta(days=dias_atras)
                start_time = start_time.replace(hour=hora_inicio, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(hours=2)
                
                Reservation.objects.create(
                    user=usuario,
                    room=sala,
                    start_time=start_time,
                    end_time=end_time,
                    purpose="Clase de demostración",
                    status='completed'
                )
                
            except Exception:
                continue
