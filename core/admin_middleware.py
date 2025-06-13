from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
import re
import logging

logger = logging.getLogger(__name__)

class AdminSecurityMiddleware:
    """
    Middleware especializado en proteger rutas administrativas.
    
    Proporciona verificación más estricta para rutas administrativas
    y complementa al SecurityMiddleware general.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Patrones de URL administrativas que requieren protección especial
        self.admin_patterns = [
            (r'^/rooms/admin/?$', "Acceso restringido: solo administradores pueden acceder."),
            (r'^/admin/?$', "Acceso restringido: panel de administración."),
            (r'^/admin/.*', "Acceso restringido: panel de administración."),
            (r'.*/admin/.*', "Acceso restringido: área administrativa."),
        ]
        
        # Compilar las expresiones regulares
        self.compiled_patterns = [(re.compile(pattern), message) 
                                for pattern, message in self.admin_patterns]
        
    def __call__(self, request):
        """Procesar la solicitud y aplicar la lógica de seguridad."""
        try:
            path = request.path
            
            # Verificar si la sesión está marcada como cerrada
            if request.session.get('is_logged_out', False):
                last_username = request.session.get('last_username', 'desconocido')
                logger.warning(
                    f"[SEGURIDAD_ADMIN] ALERTA: Intento de acceso con sesión cerrada a ruta administrativa: "
                    f"Usuario '{last_username}' desde IP {self.get_client_ip(request)}. "
                    f"Posible uso del botón 'atrás' después de cerrar sesión. "
                    f"URL solicitada: {path} [Demostración de Seguridad]"
                )
                request.session.flush()
                messages.warning(
                    request,
                    "¡Sesión cerrada detectada! Por seguridad, se ha bloqueado el acceso a ruta administrativa. "
                    "Inicia sesión nuevamente para continuar. [Demostración de Seguridad]"
                )
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            
            # Verificar si la ruta coincide con algún patrón administrativo
            is_admin_path = False
            admin_message = ""
            
            for pattern, message in self.compiled_patterns:
                if pattern.match(path):
                    is_admin_path = True
                    admin_message = message
                    break
                    
            # Si es una ruta admin, aplicar verificaciones adicionales
            if is_admin_path:
                # Si no está autenticado, redirigir al login
                if not request.user.is_authenticated:
                    logger.warning(
                        f"[SEGURIDAD_ADMIN] ALERTA: Intento de acceso no autenticado a ruta administrativa: "
                        f"URL: {path} desde IP: {self.get_client_ip(request)} [Demostración de Seguridad]"
                    )
                    return redirect(f"{settings.LOGIN_URL}?next={request.path}")
                    
                # Si está autenticado pero no es admin ni superusuario
                if not (hasattr(request.user, 'role') and 
                        (request.user.is_superuser or 
                         (hasattr(request.user, 'is_admin') and request.user.is_admin) or 
                         (hasattr(request.user, 'role') and request.user.role == 'admin'))):
                    logger.warning(
                        f"[SEGURIDAD_ADMIN] ALERTA: Intento de acceso no autorizado a ruta administrativa: "
                        f"Usuario {request.user.username} con rol '{getattr(request.user, 'role', 'desconocido')}' "
                        f"intentó acceder a {path} [Demostración de Seguridad]"
                    )
                    from django.core.exceptions import PermissionDenied
                    raise PermissionDenied(admin_message)
            
            # Continuar con el proceso normal si pasa todas las verificaciones
            return self.get_response(request)
            
        except Exception as e:
            logger.error(f"[SEGURIDAD_ADMIN] Error en AdminSecurityMiddleware: {str(e)}", exc_info=True)
            return self.get_response(request)
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente, considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip