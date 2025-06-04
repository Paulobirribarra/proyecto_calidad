"""
Vistas para la gestión de salas de estudio.

Este módulo contiene todas las vistas para el manejo de salas,
reservas y reseñas, con manejo completo de errores y logging.

REQ-008: Manejo de errores y excepciones
REQ-009: Logging y análisis de errores
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta, time
import logging

from .models import Room, Reservation, Review
from .forms import RoomForm, ReservationForm, ReviewForm, RoomSearchForm

logger = logging.getLogger(__name__)


def is_admin(user):
    """Verificar si el usuario es administrador."""
    return user.is_authenticated and (user.is_admin() or user.is_staff)


def handle_exception(view_func):
    """
    Decorador para manejo centralizado de excepciones.
    
    Captura y registra errores comunes, proporcionando
    mensajes de error apropiados al usuario.
    """
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except PermissionDenied as e:
            logger.warning(
                f"Acceso denegado para usuario {request.user.username} "
                f"en vista {view_func.__name__}: {str(e)}"
            )
            messages.error(request, "No tienes permisos para realizar esta acción.")
            return redirect('rooms:room_list')
        except ValidationError as e:
            logger.error(
                f"Error de validación en {view_func.__name__}: {str(e)}"
            )
            messages.error(request, f"Error de validación: {str(e)}")
            return redirect(request.META.get('HTTP_REFERER', 'rooms:room_list'))
        except IntegrityError as e:
            logger.error(
                f"Error de integridad de datos en {view_func.__name__}: {str(e)}"
            )
            messages.error(request, "Error en la base de datos. Intenta de nuevo.")
            return redirect(request.META.get('HTTP_REFERER', 'rooms:room_list'))
        except Exception as e:
            logger.critical(
                f"Error inesperado en {view_func.__name__}: {str(e)}",
                exc_info=True
            )
            messages.error(request, "Ha ocurrido un error inesperado. Contacta al soporte.")
            return redirect('rooms:room_list')
    
    return wrapper


@handle_exception
def room_list(request):
    """
    Vista para listar y buscar salas disponibles.
    
    Permite filtrar salas por diversos criterios y
    verificar disponibilidad en tiempo real.
    """
    try:
        form = RoomSearchForm(request.GET or None)
        rooms_queryset = Room.objects.filter(is_active=True)
        
        # Aplicar filtros de búsqueda
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            min_capacity = form.cleaned_data.get('min_capacity')
            available_date = form.cleaned_data.get('available_date')
            user_role_filter = form.cleaned_data.get('user_role_filter')
            availability_filter = form.cleaned_data.get('availability_filter')
            room_type_filter = form.cleaned_data.get('room_type_filter')
            
            # Filtro por texto de búsqueda
            if search_query:
                rooms_queryset = rooms_queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(location__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            # Filtro por capacidad
            if min_capacity:
                rooms_queryset = rooms_queryset.filter(capacity__gte=min_capacity)
            
            # Filtro por rol de usuario (seleccionado explícitamente o automático)
            if request.user.is_authenticated:                # Si el usuario no ha seleccionado un filtro de rol específico,
                # aplicamos un filtro automático basado en su rol
                if not user_role_filter:
                    if hasattr(request.user, 'is_estudiante') and request.user.is_estudiante():
                        user_role = 'estudiante'
                    elif hasattr(request.user, 'is_profesor') and request.user.is_profesor():
                        user_role = 'profesor'
                    elif hasattr(request.user, 'is_admin') and request.user.is_admin():
                        user_role = 'administrador'
                    elif hasattr(request.user, 'is_staff') and request.user.is_staff:
                        user_role = 'administrador'
                    else:
                        # Rol por defecto si no se puede determinar
                        user_role = 'estudiante'
                    
                    # Actualizamos el formulario para mostrar el filtro seleccionado
                    form.initial['user_role_filter'] = user_role
                    user_role_filter = user_role
            
            # Aplicar filtro por rol (seleccionado o automático)
            if user_role_filter and request.user.is_authenticated:
                if user_role_filter == 'estudiante':
                    # Estudiantes: solo salas de estudio individuales y salas gratuitas
                    rooms_queryset = rooms_queryset.filter(
                        Q(room_type__in=['sala_estudio', 'sala_individual']) |
                        Q(hourly_rate=0)
                    )
                elif user_role_filter == 'profesor':
                    # Profesores: todas las salas excepto las restringidas para administradores
                    rooms_queryset = rooms_queryset.exclude(
                        room_type='sala_servidor'
                    )
                elif user_role_filter == 'administrador':
                    # Administradores: todas las salas (sin filtro)
                    pass
                elif user_role_filter == 'soporte':
                    # Soporte: salas técnicas y de laboratorio
                    rooms_queryset = rooms_queryset.filter(
                        room_type__in=['laboratorio', 'sala_reunion', 'auditorio']
                    )            # Filtro por tipo de sala
            if room_type_filter:
                rooms_queryset = rooms_queryset.filter(room_type=room_type_filter)
            
            # Filtro por disponibilidad
            if availability_filter:
                from django.utils import timezone
                now = timezone.now()
                
                if availability_filter == 'available_now':
                    # Salas disponibles ahora mismo
                    current_reservations = Room.objects.filter(
                        reservations__status__in=['confirmed', 'in_progress'],
                        reservations__start_time__lte=now,
                        reservations__end_time__gt=now
                    ).values_list('id', flat=True)
                    rooms_queryset = rooms_queryset.exclude(id__in=current_reservations)
                    
                    # También verificar horarios de operación
                    current_time = now.time()
                    rooms_queryset = rooms_queryset.filter(
                        opening_time__lte=current_time,
                        closing_time__gte=current_time
                    )
                
                elif availability_filter == 'available_today':
                    # Salas con al menos una hora disponible hoy
                    today = now.date()
                    today_start = timezone.make_aware(datetime.combine(today, time.min))
                    today_end = timezone.make_aware(datetime.combine(today, time.max))
                    
                    # Obtener salas completamente ocupadas hoy
                    fully_booked_today = []
                    for room in rooms_queryset:
                        room_start = timezone.make_aware(datetime.combine(today, room.opening_time))
                        room_end = timezone.make_aware(datetime.combine(today, room.closing_time))
                        
                        reservations = room.reservations.filter(
                            status__in=['confirmed', 'in_progress'],
                            start_time__date=today
                        ).order_by('start_time')
                        # Verificar si está completamente reservada
                        current_time = room_start
                        for reservation in reservations:
                            if reservation.start_time > current_time:
                                break  # Hay tiempo libre
                            current_time = max(current_time, reservation.end_time)
                        
                        if current_time >= room_end:
                            fully_booked_today.append(room.id)
                    
                    rooms_queryset = rooms_queryset.exclude(id__in=fully_booked_today)
                
                elif availability_filter == 'available_custom' and available_date:
                    # Para horario específico, solo filtrar por fecha (sin horarios específicos)
                    # Mostrar salas que tengan al menos algún tiempo disponible en esa fecha
                    pass  # Mantener todas las salas para que el usuario vea horarios disponibles
            
            # Filtro de disponibilidad por fecha específica (compatibilidad simplificada)
            elif available_date:
                # Solo filtrar por fecha, sin horarios específicos
                # El usuario puede ver la disponibilidad detallada en la página de cada sala
                pass
        
        # Filtrar salas que el usuario puede reservar antes de la paginación
        if request.user.is_authenticated:
            # Crear una lista temporaria de salas a filtrar
            filtered_rooms = []
            # Almacenar solo los IDs de las salas que el usuario puede reservar
            allowed_room_ids = []
            
            for room in rooms_queryset:
                if room.can_be_reserved_by(request.user):
                    allowed_room_ids.append(room.id)
            
            # Filtrar el queryset con los IDs permitidos
            if not (request.user.is_staff or request.user.is_superuser or
                   (hasattr(request.user, 'is_admin') and request.user.is_admin()) or
                   (hasattr(request.user, 'is_profesor') and request.user.is_profesor())):
                rooms_queryset = rooms_queryset.filter(id__in=allowed_room_ids)
        
        # Paginación después del filtrado
        paginator = Paginator(rooms_queryset.order_by('name'), 12)
        page = request.GET.get('page')
        
        try:
            rooms = paginator.page(page)
        except PageNotAnInteger:
            rooms = paginator.page(1)
        except EmptyPage:
            rooms = paginator.page(paginator.num_pages)
        logger.info(
            f"Lista de salas consultada por {request.user.username if request.user.is_authenticated else 'anónimo'}"
        )
        
        # Marcar las salas que el usuario puede reservar para mostrar/ocultar botones en la interfaz
        if request.user.is_authenticated:
            for room in rooms:
                room.user_can_reserve = room.can_be_reserved_by(request.user)
        context = {
            'rooms': rooms,
            'form': form,
            'total_rooms': rooms_queryset.count(),
            'is_paginated': paginator.num_pages > 1,
            'page_obj': rooms,
            'filtered_by_role': request.user.is_authenticated and not (
                request.user.is_staff or 
                request.user.is_superuser or 
                (hasattr(request.user, 'is_admin') and request.user.is_admin()) or
                (hasattr(request.user, 'is_profesor') and request.user.is_profesor())
            )
        }
        
        return render(request, 'rooms/room_list.html', context)
    
    except Exception as e:
        logger.error(f"Error en room_list: {str(e)}", exc_info=True)
        messages.error(request, "Error al cargar la lista de salas.")
        return render(request, 'rooms/room_list.html', {'rooms': [], 'form': RoomSearchForm()})


@handle_exception
def room_detail(request, room_id):
    """Vista detallada de una sala específica."""
    try:
        room = get_object_or_404(Room, id=room_id, is_active=True)
        # Obtener reseñas recientes a través de reservations
        from rooms.models import Review
        recent_reviews = Review.objects.filter(
            reservation__room=room
        ).select_related(
            'reservation__user'
        ).order_by('-created_at')[:5]
        
        # Obtener reservas actuales y futuras para mostrar disponibilidad
        from django.utils import timezone
        now = timezone.now()
        today = now.date()
        
        # Reservas confirmadas de hoy y próximos 7 días
        upcoming_reservations = room.reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__date__gte=today,
            start_time__date__lte=today + timezone.timedelta(days=7)
        ).order_by('start_time')
        
        # Reservas activas ahora mismo
        current_reservations = room.reservations.filter(
            status__in=['confirmed', 'in_progress'],
            start_time__lte=now,
            end_time__gt=now
        )
        
        # Calcular estadísticas
        total_reviews = room.total_reviews
        avg_rating = room.average_rating
        
        # Verificar si el usuario actual puede reservar basado en su rol
        can_reserve = request.user.is_authenticated and room.can_be_reserved_by(request.user) if request.user.is_authenticated else False        # Determinar mensaje informativo sobre permisos
        permission_message = None
        if request.user.is_authenticated and not can_reserve:
            if request.user.is_estudiante():
                if room.room_type not in ['sala_estudio', 'sala_individual']:
                    permission_message = f"Esta sala es de tipo '{dict(Room.ROOM_TYPE_CHOICES).get(room.room_type, room.room_type)}' y no está disponible para estudiantes. Como estudiante, solo puedes reservar salas de estudio y salas individuales."
                else:
                    permission_message = f"Esta sala requiere permisos especiales que tu cuenta no tiene."
            elif request.user.is_profesor():
                if room.room_type == 'sala_servidor':
                    permission_message = f"Esta sala es de tipo '{dict(Room.ROOM_TYPE_CHOICES).get(room.room_type, room.room_type)}' y está reservada solo para personal administrativo."
                else:
                    permission_message = f"Esta sala requiere permisos especiales que tu cuenta no tiene."
            else:
                permission_message = f"No tienes permisos para reservar esta sala. Esta sala está reservada para roles específicos (roles permitidos: {room.allowed_roles})."
        
        logger.info(f"Sala {room.name} consultada por {request.user.username if request.user.is_authenticated else 'anónimo'}")
        context = {
            'room': room,
            'recent_reviews': recent_reviews,
            'total_reviews': total_reviews,
            'avg_rating': avg_rating,
            'can_reserve': can_reserve,
            'permission_message': permission_message,
            'upcoming_reservations': upcoming_reservations,
            'current_reservations': current_reservations,
            'has_current_reservation': current_reservations.exists()
        }
        
        return render(request, 'rooms/room_detail.html', context)
    
    except Http404:
        logger.warning(f"Intento de acceso a sala inexistente: ID {room_id}")
        messages.error(request, "La sala solicitada no existe.")
        return redirect('rooms:room_list')


@login_required
@handle_exception
def room_reserve(request, room_id):
    """Vista para reservar una sala."""
    try:
        room = get_object_or_404(Room, id=room_id, is_active=True)
        
        # Verificar si el usuario puede reservar esta sala según su rol
        if not room.can_be_reserved_by(request.user):
            logger.warning(
                f"Intento de reserva no autorizado: Usuario {request.user.username} "
                f"con rol {request.user.role} intentó reservar {room.name}"
            )
            messages.error(
                request, 
                f"No tienes permisos para reservar esta sala ({room.name}). "
                f"Esta sala solo está disponible para ciertos roles de usuario."
            )
            return redirect('rooms:room_detail', room_id=room_id)
        
        if request.method == 'POST':
            form = ReservationForm(request.POST, user=request.user)
            # Asignar la sala antes de validar
            form.instance.room = room
            
            if form.is_valid():
                with transaction.atomic():
                    reservation = form.save(commit=False)
                    reservation.user = request.user
                    reservation.room = room  # Asegurar que la sala se asigne correctamente
                    reservation.status = 'confirmed'
                    reservation.save()
                    
                    logger.info(
                        f"Nueva reserva creada: {reservation.room.name} "
                        f"por {request.user.username} "
                        f"({reservation.start_time} - {reservation.end_time})"
                    )
                    
                    messages.success(
                        request, 
                        f"¡Reserva confirmada! Has reservado {room.name} "
                        f"el {reservation.start_time.strftime('%d/%m/%Y de %H:%M')} "
                        f"a {reservation.end_time.strftime('%H:%M')}."
                    )
                    
                    return redirect('rooms:reservation_detail', reservation_id=reservation.id)
            else:
                logger.warning(
                    f"Error en formulario de reserva por {request.user.username}: "
                    f"{form.errors}"
                )
        else:
            # Pre-llenar con valores sugeridos
            initial_data = {'room': room}
            
            # Sugerir horario (próxima hora disponible)
            now = timezone.now()
            suggested_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            suggested_end = suggested_start + timedelta(hours=2)
            
            initial_data.update({
                'start_time': suggested_start,
                'end_time': suggested_end,
                'attendees_count': 1
            })
            
            form = ReservationForm(initial=initial_data, user=request.user)
        
        context = {
            'room': room,
            'form': form
        }
        
        return render(request, 'rooms/room_reserve.html', context)
    
    except Exception as e:
        logger.error(f"Error en room_reserve: {str(e)}", exc_info=True)
        messages.error(request, "Error al procesar la reserva.")
        return redirect('rooms:room_detail', room_id=room_id)


@login_required
@handle_exception
def reservation_list(request):
    """Vista para listar las reservas del usuario actual."""
    try:
        # Primero obtenemos todas las reservas del usuario
        reservations_queryset = request.user.reservations.all().select_related('room')
        
        # Actualizar automáticamente el estado de las reservas pasadas
        # que tengan status 'confirmed' y su end_time ya pasó
        now = timezone.now()
        updated_count = 0
        for reservation in reservations_queryset:
            if reservation.status == 'confirmed' and now > reservation.end_time:
                reservation.status = 'completed'
                reservation.save(update_fields=['status'])
                updated_count += 1
        
        if updated_count > 0:
            logger.info(f"Se actualizaron automáticamente {updated_count} reservas a 'completed'")
            messages.info(request, f"Se actualizaron {updated_count} reservas completadas.")
        
        # Filtrar por estado si se especifica
        status_filter = request.GET.get('status')
        if status_filter and status_filter in dict(Reservation.STATUS_CHOICES):
            reservations_queryset = reservations_queryset.filter(status=status_filter)
        
        # Ordenar por fecha de inicio (más recientes primero)
        reservations_queryset = reservations_queryset.order_by('-start_time')
        
        # Paginación
        paginator = Paginator(reservations_queryset, 10)
        page = request.GET.get('page')
        
        try:
            reservations = paginator.page(page)
        except PageNotAnInteger:
            reservations = paginator.page(1)
        except EmptyPage:
            reservations = paginator.page(paginator.num_pages)
        
        context = {
            'reservations': reservations,
            'status_choices': Reservation.STATUS_CHOICES,
            'current_status': status_filter
        }
        
        return render(request, 'rooms/reservation_list.html', context)
    
    except Exception as e:
        logger.error(f"Error en reservation_list: {str(e)}", exc_info=True)
        messages.error(request, "Error al cargar las reservas.")
        return render(request, 'rooms/reservation_list.html', {'reservations': []})


@login_required
@handle_exception
def reservation_detail(request, reservation_id):
    """Vista para mostrar los detalles de una reserva específica."""
    try:
        # Solo permitir que el usuario vea sus propias reservas (o admin)
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user
        )
        
        logger.info(f"Detalles de reserva #{reservation_id} consultados por {request.user.username}")
        
        context = {
            'reservation': reservation,
        }
        
        return render(request, 'rooms/reservation_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error en reservation_detail: {str(e)}")
        messages.error(request, "Error al cargar los detalles de la reserva.")
        return redirect('rooms:reservation_list')


@login_required
@handle_exception
def reservation_cancel(request, reservation_id):
    """Vista para cancelar una reserva."""
    try:
        # Solo permitir que el usuario cancele sus propias reservas
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user,
            status='confirmed'
        )
        
        # Verificar si la reserva se puede cancelar (30 minutos antes)
        if not reservation.can_be_cancelled():
            messages.error(
                request, 
                "No puedes cancelar esta reserva. Las reservas solo se pueden "
                "cancelar hasta 30 minutos antes del horario de inicio."
            )
            return redirect('rooms:reservation_detail', reservation_id=reservation_id)
        
        if request.method == 'POST':
            with transaction.atomic():
                reservation.status = 'cancelled'
                reservation.save()
                
                logger.info(
                    f"Reserva #{reservation_id} cancelada por {request.user.username} "
                    f"- Sala: {reservation.room.name}"
                )
                
                messages.success(
                    request, 
                    f"Reserva cancelada exitosamente. La sala {reservation.room.name} "
                    f"ya está disponible para el horario {reservation.start_time.strftime('%d/%m/%Y %H:%M')}."
                )
                
                return redirect('rooms:reservation_list')
        
        # Si no es POST, mostrar confirmación
        context = {
            'reservation': reservation,
        }
        
        return render(request, 'rooms/reservation_cancel_confirm.html', context)
        
    except Exception as e:
        logger.error(f"Error en reservation_cancel: {str(e)}")
        messages.error(request, "Error al cancelar la reserva.")
        return redirect('rooms:reservation_list')


@login_required
@handle_exception
def room_review(request, reservation_id):
    """Vista para calificar una sala después de una reserva."""
    try:
        # Primero, obtener la reserva del usuario (sin filtrar por estado)
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user
        )
        
        # Actualizar automáticamente el estado de la reserva si ya ha terminado
        now = timezone.now()
        if reservation.status == 'confirmed' and now > reservation.end_time:
            reservation.status = 'completed'
            reservation.save(update_fields=['status'])
            logger.info(f"Reserva #{reservation.id} actualizada automáticamente a 'completed' en room_review")
        
        # Verificar que la reserva esté completada
        if reservation.status != 'completed':
            messages.warning(request, 
                "Solo puedes calificar reservas completadas. Esta reserva tiene estado: "
                f"{dict(Reservation.STATUS_CHOICES).get(reservation.status, reservation.status)}."
            )
            return redirect('rooms:reservation_detail', reservation_id=reservation_id)
        
        # Verificar que no exista ya una reseña
        if hasattr(reservation, 'review'):
            messages.info(request, "Ya has calificado esta reserva.")
            return redirect('rooms:reservation_detail', reservation_id=reservation_id)
        
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                with transaction.atomic():
                    review = form.save(commit=False)
                    review.reservation = reservation
                    # Llamar clean() manualmente para evitar problemas de validación
                    try:
                        review.clean()
                        review.save()
                        
                        logger.info(
                            f"Nueva reseña creada para {reservation.room.name} "
                            f"por {request.user.username} - Rating: {review.rating}"
                        )
                        
                        messages.success(
                            request, 
                            f"¡Gracias por tu reseña! Has calificado {reservation.room.name} "
                            f"con {review.rating} estrella{'s' if review.rating != 1 else ''}."
                        )
                        
                        return redirect('rooms:reservation_detail', reservation_id=reservation_id)
                        
                    except ValidationError as e:
                        logger.error(f"Error de validación al crear reseña: {str(e)}")
                        form.add_error(None, str(e))
                        messages.error(request, f"Error al crear la reseña: {str(e)}")
        else:
            form = ReviewForm()
        
        context = {
            'reservation': reservation,
            'form': form,
            'room': reservation.room
        }
        
        return render(request, 'rooms/room_review.html', context)
        
    except Exception as e:
        logger.error(f"Error en room_review: {str(e)}")
        messages.error(request, "Error al procesar la calificación.")
        return redirect('rooms:reservation_list')


# Vistas para administradores

@user_passes_test(is_admin)
@handle_exception
def admin_room_create(request):
    """Vista para crear una nueva sala (solo administradores)."""
    try:
        # Verificación adicional de seguridad para prevenir escalada de privilegios
        if not request.user.is_admin() and not request.user.is_superuser:
            logger.warning(
                f"Intento de acceso no autorizado a admin_room_create: Usuario {request.user.username} "
                f"con rol '{request.user.role}'"
            )
            raise PermissionDenied("No tienes permisos para crear salas.")
            
        if request.method == 'POST':
            form = RoomForm(request.POST)
            
            if form.is_valid():
                with transaction.atomic():
                    room = form.save(commit=False)
                    room.created_by = request.user
                    room.save()
                    
                    logger.info(f"Nueva sala creada: {room.name} por {request.user.username}")
                    
                    messages.success(request, f"Sala '{room.name}' creada exitosamente.")
                    return redirect('rooms:room_detail', room_id=room.id)
        else:
            form = RoomForm()
        
        context = {'form': form}
        return render(request, 'rooms/admin/room_create.html', context)
    
    except PermissionDenied as e:
        logger.warning(f"Acceso denegado: {str(e)}")
        messages.error(request, str(e))
        return redirect('rooms:room_list')
    except Exception as e:
        logger.error(f"Error en admin_room_create: {str(e)}", exc_info=True)
        messages.error(request, "Error al crear la sala.")
        return redirect('rooms:room_list')


@user_passes_test(is_admin)
@handle_exception
def admin_room_edit(request, room_id):
    """Vista para editar una sala existente (solo administradores)."""
    try:
        # Verificación adicional de seguridad para prevenir escalada de privilegios
        if not request.user.is_admin() and not request.user.is_superuser:
            logger.warning(
                f"Intento de acceso no autorizado a admin_room_edit: Usuario {request.user.username} "
                f"con rol '{request.user.role}' intentó editar sala {room_id}"
            )
            raise PermissionDenied("No tienes permisos para editar salas.")
            
        room = get_object_or_404(Room, id=room_id)
        
        if request.method == 'POST':
            form = RoomForm(request.POST, instance=room)
            
            if form.is_valid():
                with transaction.atomic():
                    room = form.save()
                    
                    logger.info(f"Sala editada: {room.name} por {request.user.username}")
                    
                    messages.success(request, f"Sala '{room.name}' actualizada exitosamente.")
                    return redirect('rooms:room_detail', room_id=room.id)
        else:
            form = RoomForm(instance=room)
        
        context = {
            'form': form,
            'room': room
        }
        
        return render(request, 'rooms/admin/room_edit.html', context)
    
    except Exception as e:
        logger.error(f"Error en admin_room_edit: {str(e)}", exc_info=True)
        messages.error(request, "Error al editar la sala.")
        return redirect('rooms:room_detail', room_id=room_id)


# API endpoints para AJAX

@login_required
def api_room_availability(request, room_id):
    """
    API endpoint para verificar disponibilidad de sala.
    
    Retorna información de disponibilidad en formato JSON
    para uso con JavaScript en el frontend.
    """
    try:
        room = get_object_or_404(Room, id=room_id, is_active=True)
        
        date_str = request.GET.get('date')
        start_time_str = request.GET.get('start_time')
        end_time_str = request.GET.get('end_time')
        
        if not all([date_str, start_time_str, end_time_str]):
            return JsonResponse({
                'available': False,
                'error': 'Parámetros requeridos: date, start_time, end_time'
            })
        
        # Parsear fecha y horas
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        
        start_datetime = datetime.combine(date_obj, start_time_obj)
        end_datetime = datetime.combine(date_obj, end_time_obj)
        
        # Verificar disponibilidad
        is_available = room.is_available_at(start_datetime, end_datetime)
        
        response_data = {
            'available': is_available,
            'room_name': room.name,
            'capacity': room.capacity
        }
        
        if not is_available:
            # Encontrar conflictos específicos
            conflicts = room.reservations.filter(
                status__in=['confirmed', 'in_progress'],
                start_time__lt=end_datetime,
                end_time__gt=start_datetime
            ).values(
                'start_time', 'end_time', 'user__username'
            )
            
            response_data['conflicts'] = list(conflicts)
        
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error(f"Error en api_room_availability: {str(e)}")
        return JsonResponse({
            'available': False,
            'error': 'Error al verificar disponibilidad'
        })


@handle_exception
def error_404(request, exception):
    """Vista personalizada para error 404."""
    logger.warning(f"Error 404 - URL no encontrada: {request.path}")
    return render(request, 'errors/404.html', status=404)


@handle_exception
def error_500(request):
    """Vista personalizada para error 500."""
    logger.error(f"Error 500 - Error interno del servidor en: {request.path}")
    return render(request, 'errors/500.html', status=500)
