from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.conf import settings
import logging
import random

logger = logging.getLogger(__name__)

class SessionSecurityMiddleware:
    """
    Middleware que refuerza la seguridad de las sesiones.
    
    Previene:
    1. Acceso no autorizado después de cerrar sesión mediante botón "atrás"
    2. Reutilización de sesiones expiradas
    3. Uso de cookies de sesión después de cierre de sesión
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def get_client_ip(self, request):
        """Obtener la IP real del cliente, considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    def __call__(self, request):
        """Procesar la solicitud HTTP y aplicar validaciones de seguridad de sesión."""
        
        # LOG DE DEPURACIÓN para la demostración
        logger.info(f"[DEBUG] Procesando solicitud: {request.path}, Usuario autenticado: {request.user.is_authenticated}, Session keys: {list(request.session.keys())}")
        
        # PRIMERA VERIFICACIÓN: Detectar intentos de acceso post-logout
        if request.session.get('is_logged_out', False):
            last_username = request.session.get('last_username', 'desconocido')
            ip_address = self.get_client_ip(request)
            logger.warning(
                f"[SEGURIDAD_SESIÓN] ALERTA: Intento de acceso con sesión cerrada detectado: "
                f"Usuario '{last_username}' desde IP {ip_address}. "
                f"Posible uso del botón 'atrás' después de cerrar sesión. "
                f"URL solicitada: {request.path} [Demostración de Seguridad]"
            )
            # Limpiar completamente la sesión
            request.session.flush()
            messages.warning(
                request,
                "¡Sesión cerrada detectada! Por seguridad, se ha bloqueado el acceso. "
                "Inicia sesión nuevamente para continuar. [Demostración de Seguridad]"
            )
            return redirect(settings.LOGIN_URL)
        
        # SEGUNDA VERIFICACIÓN: Si el usuario está autenticado, verificar la validez de la sesión
        if request.user.is_authenticated:
            # Guardar el nombre de usuario en la sesión para referencia futura
            request.session['last_username'] = request.user.username
            
            # Verificar si la sesión tiene una marca de tiempo de última actividad
            if not request.session.get('last_activity'):
                username = request.user.username
                ip_address = self.get_client_ip(request)
                logger.warning(
                    f"[SEGURIDAD_SESIÓN] ALERTA: Acceso post-logout detectado: "
                    f"Usuario '{username}' desde IP {ip_address}. "
                    f"Intento de navegación usando botón 'atrás' bloqueado. "
                    f"URL: {request.path} [Demostración de Seguridad]"
                )
                logout(request)
                # Crear una nueva sesión para almacenar banderas post-logout
                request.session['is_logged_out'] = True
                request.session['last_username'] = username
                request.session['last_activity'] = None
                request.session.modified = True
                messages.warning(
                    request,
                    "¡Sesión inválida detectada! Posible uso del botón 'atrás'. "
                    "Inicia sesión nuevamente para continuar. [Demostración de Seguridad]"
                )
                return redirect(settings.LOGIN_URL)
        
        # Procesar la solicitud normalmente
        response = self.get_response(request)
        
        # Configurar encabezados de caché para páginas protegidas
        if request.user.is_authenticated:
            # Actualizar la marca de tiempo de última actividad
            request.session['last_activity'] = True
            
            # Registrar ocasionalmente la navegación activa del usuario (10% de probabilidad)
            if random.randint(1, 10) == 1:
                username = request.user.username
                ip_address = self.get_client_ip(request)
                logger.info(
                    f"[SEGURIDAD_SESIÓN] Usuario '{username}' navegando con sesión válida, "
                    f"URL: {request.path}, IP: {ip_address}"
                )
            
            # Establecer encabezados anti-caché para evitar almacenamiento en caché
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response