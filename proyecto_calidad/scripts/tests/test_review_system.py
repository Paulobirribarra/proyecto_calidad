#!/usr/bin/env python
"""
Test completo del sistema de valoración de salas.

Este script prueba todo el flujo de creación de reseñas:
1. Usuario con reserva completada
2. Acceso a la URL de valoración
3. Envío del formulario de valoración
4. Verificación de la reseña creada

Ejecutar con: python test_review_system.py
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar después de configurar Django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rooms.models import Room, Reservation, Review
from rooms.forms import ReviewForm

User = get_user_model()

def test_review_system():
    """Test completo del sistema de valoración"""
    
    print("🔍 Iniciando test del sistema de valoración...")
    
    # 1. Verificar que tenemos usuarios y reservas
    print("\n1. Verificando datos existentes...")
    
    usuarios = User.objects.all()
    reservas = Reservation.objects.filter(status='completed')
    salas = Room.objects.filter(is_active=True)
    
    print(f"   - Usuarios en sistema: {usuarios.count()}")
    print(f"   - Reservas completadas: {reservas.count()}")
    print(f"   - Salas activas: {salas.count()}")
    
    if reservas.count() == 0:
        print("❌ No hay reservas completadas para probar")
        return False
    
    # 2. Seleccionar una reserva de prueba
    reserva_test = reservas.first()
    usuario_test = reserva_test.user
    sala_test = reserva_test.room
    
    print(f"\n2. Reserva seleccionada para test:")
    print(f"   - ID: {reserva_test.id}")
    print(f"   - Usuario: {usuario_test.username} ({usuario_test.role})")
    print(f"   - Sala: {sala_test.name}")
    print(f"   - Estado: {reserva_test.status}")
    print(f"   - Fecha: {reserva_test.start_time.strftime('%d/%m/%Y %H:%M')}")
    
    # 3. Verificar que no tiene reseña existente
    print(f"\n3. Verificando si ya tiene reseña...")
    if hasattr(reserva_test, 'review'):
        print(f"   ⚠️  La reserva ya tiene una reseña. Eliminándola para el test...")
        reserva_test.review.delete()
    else:
        print(f"   ✅ La reserva no tiene reseña previa")
    
    # 4. Test del formulario de reseña
    print(f"\n4. Probando formulario de reseña...")
    
    datos_formulario = {
        'rating': 4,
        'cleanliness_rating': 5,
        'equipment_rating': 4,
        'comfort_rating': 3,
        'comment': 'Excelente sala de estudio, muy cómoda y con buena iluminación.',
        'comment_type': 'positive'
    }
    
    form = ReviewForm(data=datos_formulario)
    if form.is_valid():
        print(f"   ✅ Formulario válido")
        print(f"   - Datos: {form.cleaned_data}")
    else:
        print(f"   ❌ Formulario inválido: {form.errors}")
        return False
    
    # 5. Test de creación manual de reseña
    print(f"\n5. Probando creación manual de reseña...")
    
    try:
        # Crear reseña manualmente
        review = Review(
            reservation=reserva_test,
            rating=datos_formulario['rating'],
            cleanliness_rating=datos_formulario['cleanliness_rating'],
            equipment_rating=datos_formulario['equipment_rating'],
            comfort_rating=datos_formulario['comfort_rating'],
            comment=datos_formulario['comment'],
            comment_type=datos_formulario['comment_type']
        )
        
        # Intentar validar
        print(f"   - Validando modelo...")
        review.clean()
        
        # Intentar guardar
        print(f"   - Guardando en base de datos...")
        review.save()
        
        print(f"   ✅ Reseña creada exitosamente (ID: {review.id})")
        print(f"   - Rating promedio específico: {review.average_specific_rating}")
        print(f"   - Tipo de comentario: {review.get_comment_type_display()}")
        
        # Limpiar para siguientes tests
        review.delete()
        
    except Exception as e:
        print(f"   ❌ Error al crear reseña manualmente: {str(e)}")
        print(f"   - Tipo de error: {type(e).__name__}")
        return False
    
    # 6. Test con cliente web (simulando POST request)
    print(f"\n6. Probando con cliente web...")
    
    client = Client()
    
    # Hacer login
    client.force_login(usuario_test)
    
    # URL de la reseña
    url_review = reverse('rooms:room_review', kwargs={'reservation_id': reserva_test.id})
    print(f"   - URL: {url_review}")
    
    # GET request (cargar formulario)
    print(f"   - Cargando formulario...")
    response_get = client.get(url_review)
    print(f"   - Status GET: {response_get.status_code}")
    
    if response_get.status_code != 200:
        print(f"   ❌ Error al cargar formulario: {response_get.status_code}")
        if hasattr(response_get, 'content'):
            print(f"   - Contenido: {response_get.content[:500]}")
        return False
    
    # POST request (enviar reseña)
    print(f"   - Enviando reseña...")
    response_post = client.post(url_review, datos_formulario)
    print(f"   - Status POST: {response_post.status_code}")
    
    if response_post.status_code == 302:
        print(f"   ✅ Redirección exitosa (reseña creada)")
        print(f"   - Redirect URL: {response_post.url}")
    else:
        print(f"   ❌ Error en POST request")
        if hasattr(response_post, 'content'):
            content = response_post.content.decode('utf-8')
            print(f"   - Contenido: {content[:1000]}")
        return False
    
    # 7. Verificar que la reseña se creó
    print(f"\n7. Verificando reseña creada...")
    
    try:
        reserva_test.refresh_from_db()
        if hasattr(reserva_test, 'review'):
            review_creada = reserva_test.review
            print(f"   ✅ Reseña creada exitosamente")
            print(f"   - ID: {review_creada.id}")
            print(f"   - Rating: {review_creada.rating}")
            print(f"   - Comentario: {review_creada.comment}")
            print(f"   - Tipo: {review_creada.get_comment_type_display()}")
            print(f"   - Promedio específico: {review_creada.average_specific_rating}")
        else:
            print(f"   ❌ No se encontró la reseña creada")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al verificar reseña: {str(e)}")
        return False
    
    print(f"\n🎉 Test completado exitosamente!")
    return True

def test_edge_cases():
    """Test de casos límite"""
    
    print(f"\n🔬 Probando casos límite...")
    
    # Test con reserva no completada
    print(f"\n1. Test con reserva no completada...")
    reserva_pendiente = Reservation.objects.filter(status='confirmed').first()
    
    if reserva_pendiente:
        print(f"   - Reserva ID: {reserva_pendiente.id} (estado: {reserva_pendiente.status})")
        
        try:
            review = Review(
                reservation=reserva_pendiente,
                rating=5,
                cleanliness_rating=5,
                equipment_rating=5,
                comfort_rating=5,
                comment="Test con reserva no completada",
                comment_type='neutral'
            )
            review.clean()
            print(f"   ❌ No debería validar reserva no completada")
            return False
        except Exception as e:
            print(f"   ✅ Error esperado: {str(e)}")
    
    # Test con calificaciones inválidas
    print(f"\n2. Test con calificaciones inválidas...")
    reserva_completada = Reservation.objects.filter(status='completed').first()
    
    if reserva_completada and not hasattr(reserva_completada, 'review'):
        try:
            review = Review(
                reservation=reserva_completada,
                rating=6,  # Inválido
                cleanliness_rating=5,
                equipment_rating=5,
                comfort_rating=5,
                comment="Test con calificación inválida",
                comment_type='neutral'
            )
            review.clean()
            review.save()
            print(f"   ❌ No debería permitir rating > 5")
            return False
        except Exception as e:
            print(f"   ✅ Error esperado para rating inválido: {str(e)}")
    
    print(f"\n✅ Casos límite pasaron correctamente")
    return True

def mostrar_estadisticas():
    """Mostrar estadísticas del sistema"""
    
    print(f"\n📊 Estadísticas del sistema:")
    
    # Reservas por estado
    print(f"\nReservas por estado:")
    for estado, nombre in Reservation.STATUS_CHOICES:
        count = Reservation.objects.filter(status=estado).count()
        print(f"   - {nombre}: {count}")
    
    # Reseñas existentes
    total_reviews = Review.objects.count()
    print(f"\nReseñas:")
    print(f"   - Total: {total_reviews}")
    
    if total_reviews > 0:
        # Promedio por tipo de comentario
        for tipo, nombre in Review.COMMENT_TYPE_CHOICES:
            count = Review.objects.filter(comment_type=tipo).count()
            if count > 0:
                avg_rating = Review.objects.filter(comment_type=tipo).aggregate(
                    avg=django.db.models.Avg('rating')
                )['avg']
                print(f"   - {nombre}: {count} reseñas (promedio: {avg_rating:.1f})")
    
    # Reservas sin reseña
    reservas_completadas = Reservation.objects.filter(status='completed').count()
    reservas_con_review = Reservation.objects.filter(
        status='completed',
        review__isnull=False
    ).count()
    reservas_sin_review = reservas_completadas - reservas_con_review
    
    print(f"\nReservas completadas sin reseña: {reservas_sin_review}/{reservas_completadas}")

if __name__ == '__main__':
    print("=" * 60)
    print("TEST DEL SISTEMA DE VALORACIÓN DE SALAS")
    print("=" * 60)
    
    # Importar Django models después de setup
    import django.db.models
    
    try:
        # Mostrar estadísticas iniciales
        mostrar_estadisticas()
        
        # Ejecutar test principal
        if test_review_system():
            print(f"\n🎯 Test principal: ✅ PASÓ")
        else:
            print(f"\n🎯 Test principal: ❌ FALLÓ")
            sys.exit(1)
        
        # Ejecutar tests de casos límite
        if test_edge_cases():
            print(f"\n🎯 Tests casos límite: ✅ PASARON")
        else:
            print(f"\n🎯 Tests casos límite: ❌ FALLARON")
            sys.exit(1)
        
        # Mostrar estadísticas finales
        mostrar_estadisticas()
        
        print(f"\n🏆 TODOS LOS TESTS PASARON EXITOSAMENTE!")
        
    except Exception as e:
        print(f"\n💥 Error crítico en el test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
