"""
Vistas para la gestión de usuarios y autenticación.

Este módulo contiene las vistas para registro, login, logout
y gestión de perfiles de usuario.

REQ-010: Sistema de autenticación con roles
REQ-011: Gestión de perfiles de usuario
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm, ProfileForm
from rooms.models import Room

logger = logging.getLogger(__name__)


def user_login(request):
    """
    Vista para el login de usuarios.
    
    Maneja la autenticación de usuarios con validación
    de credenciales y redirección apropiada.
    """
    if request.user.is_authenticated:
        return redirect('rooms:room_list')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # Obtener información adicional para el log
                    ip_address = request.META.get('REMOTE_ADDR', 'desconocida')
                    user_agent = request.META.get('HTTP_USER_AGENT', 'desconocido')
                    
                    # Realizar login estándar de Django
                    login(request, user)
                    
                    # Configurar duración de sesión basada en "recordar datos"
                    if remember_me:
                        # Sesión de 30 días si el usuario marca "recordar"
                        request.session.set_expiry(30 * 24 * 60 * 60)  # 30 días en segundos
                        logger.info(f"[SEGURIDAD_SESIÓN] Sesión extendida activada para usuario '{username}' (30 días)")
                    else:
                        # Sesión expira al cerrar el navegador
                        request.session.set_expiry(0)
                        logger.info(f"[SEGURIDAD_SESIÓN] Sesión temporal activada para usuario '{username}' (hasta cerrar navegador)")
                    
                    # Marcar la sesión como activa
                    request.session['last_activity'] = True
                    request.session['is_logged_out'] = False
                    request.session.modified = True
                    
                    # Registrar inicio de sesión con detalles para la demostración
                    session_id = request.session.session_key
                    logger.info(f"[SEGURIDAD_SESIÓN] Inicio de sesión exitoso: Usuario '{username}', IP {ip_address}, Sesión ID {session_id}")
                    
                    # Redirección basada en el parámetro 'next' o página por defecto
                    next_url = request.GET.get('next', 'rooms:room_list')
                    
                    messages.success(
                        request, 
                        f"¡Bienvenido de vuelta, {user.first_name or user.username}!"
                    )
                    
                    return redirect(next_url)
                else:
                    logger.warning(f"Intento de login con cuenta inactiva: {username}")
                    messages.error(request, "Tu cuenta está desactivada.")
            else:
                logger.warning(f"Intento de login fallido para usuario: {username}")
                messages.error(request, "Credenciales inválidas.")
        else:
            logger.warning(f"Formulario de login inválido: {form.errors}")
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'Iniciar Sesión'
    }
    
    return render(request, 'usuarios/login.html', context)


def user_register(request):
    """
    Vista para el registro de nuevos usuarios.
    
    Permite a usuarios nuevos crear una cuenta
    con validaciones de seguridad.
    """
    if request.user.is_authenticated:
        return redirect('rooms:room_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.role = 'estudiante'  # Por defecto todos son estudiantes
                    user.is_active = True
                    user.is_staff = False  # Asegurar que no sea staff
                    user.is_superuser = False  # Asegurar que no sea superuser
                    user.save()
                    
                    # Auto-login después del registro
                    login(request, user)
                    
                    logger.info(f"Nuevo usuario registrado: {user.username}")
                    
                    messages.success(
                        request,
                        f"¡Cuenta creada exitosamente! Bienvenido, {user.first_name or user.username}."
                    )
                    
                    # Enviar email de bienvenida (opcional)
                    if user.email and hasattr(settings, 'EMAIL_HOST'):
                        try:
                            send_mail(
                                'Bienvenido al Sistema de Salas de Estudio',
                                f'Hola {user.first_name or user.username},\n\n'
                                'Tu cuenta ha sido creada exitosamente. '
                                'Ya puedes comenzar a reservar salas de estudio.',
                                settings.DEFAULT_FROM_EMAIL,
                                [user.email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            logger.warning(f"Error enviando email de bienvenida: {e}")
                    
                    return redirect('rooms:room_list')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al crear usuario: {e}")
                messages.error(request, "Error al crear la cuenta. El usuario ya existe.")
            except Exception as e:
                logger.error(f"Error inesperado al registrar usuario: {e}")
                messages.error(request, "Error inesperado. Intenta de nuevo.")
        else:
            logger.warning(f"Formulario de registro inválido: {form.errors}")
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Crear Cuenta'
    }
    
    return render(request, 'usuarios/register.html', context)


def user_logout(request):
    """
    Vista para cerrar sesión.
    
    Cierra la sesión del usuario actual y
    redirige a la página de login.
    
    Se aplican medidas de seguridad adicionales para evitar
    el acceso post-logout mediante el botón "atrás" del navegador.
    """
    if request.user.is_authenticated:
        username = request.user.username
          # Obtener información adicional para el log
        ip_address = request.META.get('REMOTE_ADDR', 'desconocida')
        user_agent = request.META.get('HTTP_USER_AGENT', 'desconocido')
        session_id = request.session.session_key
          # Realizar logout estándar de Django (esto borra la sesión)
        logout(request)
        
        # Registrar cierre de sesión con detalles para la demostración
        logger.info(f"[SEGURIDAD_SESIÓN] Cierre de sesión exitoso: Usuario '{username}', IP {ip_address}, Sesión ID {session_id}")
        logger.debug(f"Detalles adicionales de cierre sesión: Agente {user_agent}, Fecha/hora: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # DESPUÉS del logout, crear una nueva sesión para marcar el estado de logout
        request.session['is_logged_out'] = True
        request.session['last_username'] = username
        request.session['logout_timestamp'] = timezone.now().timestamp()
        request.session.modified = True
        
        messages.success(request, "Has cerrado sesión exitosamente.")
    
    response = redirect('usuarios:login')
    
    # Configurar encabezados anti-caché para la página de logout
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@login_required
def user_profile(request):
    """
    Vista para mostrar el perfil del usuario actual.
    
    Muestra información del usuario y estadísticas
    de sus reservas y actividad.
    Esta vista es de solo lectura, para ediciones usar user_profile_edit.
    """
    user = request.user
    
    # Estadísticas del usuario
    reservation_count = user.reservations.count()
    active_reservations = user.reservations.filter(
        status__in=['confirmed', 'pending'],
        start_time__gt=timezone.now()
    ).count()
    
    # Reservas recientes
    recent_reservations = user.reservations.select_related('room').order_by('-created_at')[:5]
    
    # Próximas reservas
    upcoming_reservations = user.reservations.filter(
        status__in=['confirmed', 'pending'],
        start_time__gt=timezone.now()
    ).select_related('room').order_by('start_time')[:3]
    
    context = {
        'user': user,
        'reservation_count': reservation_count,
        'active_reservations': active_reservations,
        'recent_reservations': recent_reservations,
        'upcoming_reservations': upcoming_reservations,
        'title': 'Mi Perfil'
    }
    
    return render(request, 'usuarios/profile.html', context)


@login_required
def user_profile_edit(request):
    """
    Vista para editar el perfil del usuario actual.
    
    Permite al usuario modificar su información
    personal y configuraciones.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    logger.info(f"Perfil actualizado para usuario: {user.username}")
                    
                    messages.success(request, "Perfil actualizado exitosamente.")
                    return redirect('usuarios:profile')
                    
            except Exception as e:
                logger.error(f"Error actualizando perfil: {e}")
                messages.error(request, "Error al actualizar el perfil.")
        else:
            logger.warning(f"Formulario de perfil inválido: {form.errors}")
    else:
        form = ProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'Editar Perfil'
    }
    
    return render(request, 'usuarios/profile_edit.html', context)


@login_required
def dashboard(request):
    """
    Vista del dashboard principal para usuarios autenticados.
    
    Muestra un resumen de la actividad del usuario
    y accesos rápidos a funciones principales.
    """
    user = request.user
    
    # Estadísticas generales
    total_rooms = Room.objects.filter(is_active=True).count()
    user_reservations = user.reservations.count()
    
    # Próximas reservas
    upcoming_reservations = user.reservations.filter(
        status__in=['confirmed', 'pending'],
        start_time__gt=timezone.now()
    ).select_related('room').order_by('start_time')[:3]
    
    # Salas populares (más reservadas)
    from django.db.models import Count
    popular_rooms = Room.objects.filter(
        is_active=True
    ).annotate(
        reservation_count=Count('reservations')
    ).order_by('-reservation_count')[:5]
    
    # Horarios sugeridos (basado en actividad del usuario)
    suggested_times = []
    if user_reservations > 0:
        # Análisis simple de patrones de reserva del usuario
        user_reservations_times = user.reservations.values_list('start_time__hour', flat=True)
        if user_reservations_times:
            from collections import Counter
            common_hours = Counter(user_reservations_times).most_common(3)
            suggested_times = [hour for hour, count in common_hours]
    
    context = {
        'user': user,
        'total_rooms': total_rooms,
        'user_reservations': user_reservations,
        'upcoming_reservations': upcoming_reservations,
        'popular_rooms': popular_rooms,
        'suggested_times': suggested_times,
        'title': 'Dashboard'    }
    return render(request, 'usuarios/dashboard.html', context)


@login_required
def change_password(request):
    """
    Vista para cambiar la contraseña del usuario.
    
    Permite a los usuarios cambiar su contraseña
    proporcionando la contraseña actual.
    """
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                update_session_auth_hash(request, user)  # Importante: mantiene la sesión activa
                
                messages.success(
                    request, 
                    'Tu contraseña ha sido cambiada exitosamente.'
                )
                logger.info(f"Usuario {user.username} cambió su contraseña")
                
                return redirect('usuarios:profile')
                
            except Exception as e:
                logger.error(f"Error al cambiar contraseña para {request.user.username}: {str(e)}")
                messages.error(
                    request, 
                    'Ha ocurrido un error al cambiar la contraseña. Intenta nuevamente.'
                )
        else:
            messages.error(
                request, 
                'Por favor, corrige los errores en el formulario.'
            )
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Cambiar Contraseña'
    }
    
    return render(request, 'usuarios/password_change_form.html', context)


# Vista para manejo de errores personalizadas
def custom_404(request, exception):
    """Vista personalizada para error 404."""
    logger.warning(f"Página no encontrada: {request.path}")
    return render(request, 'errors/404.html', {'title': 'Página no encontrada'}, status=404)


def custom_500(request):
    """Vista personalizada para error 500."""
    logger.error(f"Error interno del servidor: {request.path}")
    return render(request, 'errors/500.html', {'title': 'Error del servidor'}, status=500)


def custom_403(request, exception):
    """Vista personalizada para error 403."""
    logger.warning(f"Acceso prohibido: {request.path} por usuario {request.user.username if request.user.is_authenticated else 'anónimo'}")
    return render(request, 'errors/403.html', {'title': 'Acceso prohibido'}, status=403)
