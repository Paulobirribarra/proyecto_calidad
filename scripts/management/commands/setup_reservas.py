from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import Room, Reservation
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea reservas de ejemplo para demostración'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=20,
            help='Cantidad de reservas a crear (default: 20)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina reservas existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        self.stdout.write("🏫 Creando reservas de ejemplo para Colegio Clara Brincefield...")
        
        if options['reset']:
            reservas_existentes = Reservation.objects.count()
            if reservas_existentes > 0:
                Reservation.objects.all().delete()
                self.stdout.write(f"🗑️ Eliminadas {reservas_existentes} reservas existentes")
        
        # Obtener usuarios y salas
        usuarios = list(User.objects.all())
        salas = list(Room.objects.all())
        
        if not usuarios:
            self.stdout.write(self.style.ERROR("❌ No hay usuarios. Ejecuta: python manage.py setup_usuarios"))
            return
            
        if not salas:
            self.stdout.write(self.style.ERROR("❌ No hay salas. Ejecuta: python manage.py setup_colegio"))
            return
        
        cantidad = options['cantidad']
        reservas_creadas = 0
        
        # Crear reservas distribuidas en los próximos 30 días
        for i in range(cantidad):
            try:
                # Seleccionar usuario y sala al azar
                usuario = random.choice(usuarios)
                sala = random.choice(salas)
                
                # Generar fecha y hora aleatoria (próximos 30 días)
                dias_adelante = random.randint(0, 30)
                hora_inicio = random.randint(8, 18)  # Entre 8 AM y 6 PM
                duracion = random.choice([1, 2, 3])  # 1-3 horas
                
                fecha_reserva = timezone.now().date() + timedelta(days=dias_adelante)
                hora_inicio_obj = timezone.now().replace(
                    year=fecha_reserva.year,
                    month=fecha_reserva.month,
                    day=fecha_reserva.day,
                    hour=hora_inicio,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                hora_fin_obj = hora_inicio_obj + timedelta(hours=duracion)
                
                # Verificar que no haya conflicto
                conflicto = Reservation.objects.filter(
                    room=sala,
                    start_time__lt=hora_fin_obj,
                    end_time__gt=hora_inicio_obj
                ).exists()
                
                if not conflicto:
                    # Crear la reserva
                    propositos = [
                        f"Clase de {random.choice(['Matemáticas', 'Historia', 'Ciencias', 'Literatura', 'Arte'])}",
                        f"Reunión de {random.choice(['departamento', 'coordinación', 'planificación'])}",
                        f"Actividad de {random.choice(['laboratorio', 'proyecto', 'presentación'])}",
                        f"Sesión de {random.choice(['estudio', 'tutoría', 'evaluación'])}",
                    ]
                    
                    reserva = Reservation.objects.create(
                        user=usuario,
                        room=sala,
                        start_time=hora_inicio_obj,
                        end_time=hora_fin_obj,
                        purpose=random.choice(propositos),
                        status='confirmed'
                    )
                    
                    reservas_creadas += 1
                    self.stdout.write(f"   ✅ Reserva {reservas_creadas}: {usuario.username} - {sala.name}")
                    self.stdout.write(f"      📅 {fecha_reserva} de {hora_inicio}:00 a {hora_inicio + duracion}:00")
                    
            except Exception as e:
                self.stdout.write(f"   ⚠️ Error creando reserva: {e}")
                continue
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"✅ RESERVAS CREADAS: {reservas_creadas}")
        self.stdout.write("="*50)
        
        # Mostrar estadísticas por usuario
        self.stdout.write("\n📊 ESTADÍSTICAS POR USUARIO:")
        for usuario in usuarios:
            count = Reservation.objects.filter(user=usuario).count()
            if count > 0:
                self.stdout.write(f"   {usuario.username}: {count} reservas")
