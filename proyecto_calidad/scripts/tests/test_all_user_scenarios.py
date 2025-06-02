#!/usr/bin/env python
"""
Script completo para probar reservas con todos los tipos de usuarios.

Este script prueba el flujo completo de reservas para:
- Administrador (admin)
- Coordinador/Profesor (coordinador)
- Estudiante (estudiante1, estudiante2)

Verifica permisos, validaciones y funcionalidades específicas por rol.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

from rooms.models import Room, Reservation
from rooms.forms import ReservationForm

User = get_user_model()

class ReservationTester:
    """Clase para probar reservas con diferentes tipos de usuarios."""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.results = []
        
    def print_header(self, title):
        """Imprime un encabezado decorado."""
        print("\n" + "=" * 70)
        print(f"🧪 {title}")
        print("=" * 70)
    
    def print_step(self, step_number, description):
        """Imprime un paso del proceso."""
        print(f"\n{step_number}️⃣ {description}")
    
    def print_success(self, message):
        """Imprime un mensaje de éxito."""
        print(f"   ✅ {message}")
    
    def print_error(self, message):
        """Imprime un mensaje de error."""
        print(f"   ❌ {message}")
    
    def print_info(self, message):
        """Imprime un mensaje informativo."""
        print(f"   ℹ️  {message}")
    
    def get_test_users(self):
        """Obtiene los usuarios de prueba."""
        try:
            users = {
                'admin': User.objects.get(username='admin'),
                'coordinador': User.objects.get(username='coordinador'),
                'estudiante1': User.objects.get(username='estudiante1'),
                'estudiante2': User.objects.get(username='estudiante2')
            }
            return users
        except User.DoesNotExist as e:
            self.print_error(f"Usuario no encontrado: {e}")
            return None
    
    def get_test_rooms(self):
        """Obtiene las salas de prueba."""
        rooms = Room.objects.filter(is_active=True)[:3]
        return list(rooms)
    
    def create_reservation_data(self, room, hours_offset=1, duration=2):
        """Crea datos de prueba para una reserva."""
        now = timezone.now()
        start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=hours_offset)
        end_time = start_time + timedelta(hours=duration)
        
        return {
            'room': room.id,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M'),
            'attendees_count': 2,
            'purpose': f'Reserva de prueba - {room.name}',
            'notes': 'Prueba automatizada del sistema'
        }
    
    def test_user_reservation(self, user, room, scenario_name, hours_offset=1):
        """Prueba crear una reserva para un usuario específico."""
        self.print_step("🔍", f"Probando reserva para {user.username} ({scenario_name})")
        
        try:
            # 1. Verificar información del usuario
            self.print_info(f"Usuario: {user.username} - Email: {user.email}")
            if hasattr(user, 'user_type'):
                self.print_info(f"Tipo: {user.get_user_type_display()}")
            
            # 2. Crear datos del formulario
            form_data = self.create_reservation_data(room, hours_offset)
            self.print_info(f"Sala: {room.name} - Horario: {form_data['start_time']} a {form_data['end_time']}")
            
            # 3. Verificar disponibilidad de la sala
            start_datetime = datetime.strptime(form_data['start_time'], '%Y-%m-%d %H:%M')
            end_datetime = datetime.strptime(form_data['end_time'], '%Y-%m-%d %H:%M')
            
            # Convertir a timezone aware
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)
            
            is_available = room.is_available_at(start_datetime, end_datetime)
            
            if not is_available:
                self.print_error("La sala no está disponible en ese horario")
                conflicts = room.reservations.filter(
                    status__in=['confirmed', 'in_progress'],
                    start_time__lt=end_datetime,
                    end_time__gt=start_datetime
                )
                for conflict in conflicts:
                    self.print_info(f"Conflicto: {conflict.start_time} - {conflict.end_time} por {conflict.user.username}")
                return False
            
            self.print_success("Sala disponible en el horario solicitado")
            
            # 4. Probar validación del formulario
            form = ReservationForm(data=form_data, user=user)
            form.instance.room = room
            
            if not form.is_valid():
                self.print_error(f"Formulario inválido: {form.errors}")
                return False
            
            self.print_success("Formulario validado correctamente")
            
            # 5. Crear la reserva
            with transaction.atomic():
                reservation = form.save(commit=False)
                reservation.user = user
                reservation.room = room
                reservation.status = 'confirmed'
                reservation.save()
            
            self.print_success(f"Reserva #{reservation.id} creada exitosamente")
            self.print_info(f"Estado: {reservation.get_status_display()}")
            
            # 6. Verificar que se guardó correctamente
            saved_reservation = Reservation.objects.get(id=reservation.id)
            self.print_success("Reserva verificada en la base de datos")
            
            # 7. Guardar resultado
            result = {
                'user': user.username,
                'user_type': getattr(user, 'user_type', 'N/A'),
                'room': room.name,
                'reservation_id': reservation.id,
                'status': 'SUCCESS',
                'start_time': reservation.start_time,
                'end_time': reservation.end_time
            }
            self.results.append(result)
            
            return True
            
        except Exception as e:
            self.print_error(f"Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            
            result = {
                'user': user.username,
                'user_type': getattr(user, 'user_type', 'N/A'),
                'room': room.name,
                'reservation_id': None,
                'status': 'ERROR',
                'error': str(e)
            }
            self.results.append(result)
            
            return False
    
    def test_user_permissions(self, user):
        """Prueba los permisos específicos del usuario."""
        self.print_step("🔐", f"Verificando permisos para {user.username}")
        
        # Verificar si es admin
        is_admin = user.is_staff or (hasattr(user, 'is_admin') and user.is_admin())
        self.print_info(f"Es administrador: {'Sí' if is_admin else 'No'}")
        
        # Verificar autenticación
        self.print_info(f"Usuario autenticado: {'Sí' if user.is_authenticated else 'No'}")
        
        # Verificar estado activo
        self.print_info(f"Usuario activo: {'Sí' if user.is_active else 'No'}")
        
        return True
    
    def test_reservation_conflicts(self):
        """Prueba el manejo de conflictos en reservas."""
        self.print_header("PRUEBA DE CONFLICTOS EN RESERVAS")
        
        users = self.get_test_users()
        rooms = self.get_test_rooms()
        
        if not users or not rooms:
            self.print_error("No se pudieron obtener usuarios o salas para la prueba")
            return
        
        room = rooms[0]
        user1 = users['estudiante1']
        user2 = users['estudiante2']
        
        # Crear primera reserva
        self.print_step("1", "Creando primera reserva")
        success1 = self.test_user_reservation(user1, room, "Estudiante 1", hours_offset=3)
        
        # Intentar crear reserva conflictiva
        self.print_step("2", "Intentando crear reserva conflictiva")
        success2 = self.test_user_reservation(user2, room, "Estudiante 2 (Conflicto)", hours_offset=3)
        
        if success1 and not success2:
            self.print_success("Sistema maneja conflictos correctamente")
        else:
            self.print_error("Sistema NO maneja conflictos correctamente")
    
    def run_all_scenarios(self):
        """Ejecuta todos los escenarios de prueba."""
        self.print_header("INICIANDO PRUEBAS COMPLETAS DE RESERVAS")
        
        # Obtener datos de prueba
        users = self.get_test_users()
        rooms = self.get_test_rooms()
        
        if not users:
            self.print_error("No se pudieron obtener usuarios de prueba")
            return
        
        if not rooms:
            self.print_error("No se pudieron obtener salas de prueba")
            return
        
        self.print_success(f"Usuarios disponibles: {list(users.keys())}")
        self.print_success(f"Salas disponibles: {[room.name for room in rooms]}")
        
        # Escenarios de prueba
        scenarios = [
            {
                'user_key': 'admin',
                'room_index': 0,
                'name': 'Administrador',
                'hours_offset': 1
            },
            {
                'user_key': 'coordinador',
                'room_index': 1,
                'name': 'Coordinador/Profesor',
                'hours_offset': 2
            },
            {
                'user_key': 'estudiante1',
                'room_index': 2,
                'name': 'Estudiante 1',
                'hours_offset': 4
            },
            {
                'user_key': 'estudiante2',
                'room_index': 0,
                'name': 'Estudiante 2',
                'hours_offset': 6
            }
        ]
        
        # Ejecutar escenarios
        for i, scenario in enumerate(scenarios, 1):
            self.print_header(f"ESCENARIO {i}: {scenario['name']}")
            
            user = users[scenario['user_key']]
            room = rooms[scenario['room_index']]
            
            # Verificar permisos
            self.test_user_permissions(user)
            
            # Probar reserva
            self.test_user_reservation(
                user, 
                room, 
                scenario['name'], 
                scenario['hours_offset']
            )
        
        # Probar conflictos
        self.test_reservation_conflicts()
        
        # Mostrar resumen
        self.show_summary()
    
    def show_summary(self):
        """Muestra un resumen de todas las pruebas."""
        self.print_header("RESUMEN DE RESULTADOS")
        
        successful = len([r for r in self.results if r['status'] == 'SUCCESS'])
        failed = len([r for r in self.results if r['status'] == 'ERROR'])
        
        self.print_info(f"Total de pruebas: {len(self.results)}")
        self.print_success(f"Exitosas: {successful}")
        if failed > 0:
            self.print_error(f"Fallidas: {failed}")
        
        self.print_step("📊", "Detalle por usuario:")
        
        for result in self.results:
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            user_info = f"{result['user']} ({result.get('user_type', 'N/A')})"
            
            if result['status'] == 'SUCCESS':
                print(f"   {status_icon} {user_info} - Sala: {result['room']} - Reserva #{result['reservation_id']}")
                print(f"      📅 {result['start_time'].strftime('%d/%m/%Y %H:%M')} - {result['end_time'].strftime('%H:%M')}")
            else:
                print(f"   {status_icon} {user_info} - Error: {result.get('error', 'Unknown')}")
        
        # Mostrar reservas actuales en la DB
        self.show_current_reservations()
    
    def show_current_reservations(self):
        """Muestra todas las reservas actuales en la base de datos."""
        self.print_step("📋", "Reservas actuales en la base de datos:")
        
        reservations = Reservation.objects.all().order_by('-created_at')[:10]
        
        if not reservations:
            self.print_info("No hay reservas en la base de datos")
            return
        
        for reservation in reservations:
            print(f"   🎫 #{reservation.id} - {reservation.user.username} - {reservation.room.name}")
            print(f"      📅 {reservation.start_time.strftime('%d/%m/%Y %H:%M')} - {reservation.end_time.strftime('%H:%M')}")
            print(f"      📊 Estado: {reservation.get_status_display()}")
            print(f"      📝 Propósito: {reservation.purpose}")

def main():
    """Función principal del script."""
    print("🚀 Iniciando pruebas completas del sistema de reservas...")
    
    tester = ReservationTester()
    
    try:
        tester.run_all_scenarios()
        
        print("\n" + "=" * 70)
        print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
