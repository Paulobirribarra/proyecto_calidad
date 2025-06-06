"""
Middleware especializado para proteger rutas administrativas.

Este middleware está diseñado específicamente para reforzar la seguridad
de las rutas administrativas, añadiendo una capa adicional de protección
al verificar tanto el rol del usuario como los permisos específicos.
"""

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
            # Formato: (regex_pattern, mensaje_rechazo)
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
                    logger.warning(f"Intento de acceso no autenticado a ruta administrativa: {path}")
                    return redirect(f"{settings.LOGIN_URL}?next={request.path}")
                    
                # Si está autenticado pero no es admin ni superusuario
                if not (hasattr(request.user, 'role') and 
                    (request.user.is_superuser or 
                    (hasattr(request.user, 'is_admin') and request.user.is_admin()) or 
                    (hasattr(request.user, 'role') and request.user.role == 'admin'))):
                    # Registrar el intento
                    logger.warning(
                        f"Bloqueo estricto: Usuario {request.user.username} con rol "
                        f"'{getattr(request.user, 'role', 'desconocido')}' intentó acceder a {path}"
                    )
                    
                    # Lanzar PermissionDenied para mostrar la plantilla 403 personalizada
                    from django.core.exceptions import PermissionDenied
                    raise PermissionDenied(admin_message)
            
            # Continuar con el proceso normal si pasa todas las verificaciones
            return self.get_response(request)
            
        except Exception as e:
            # Registrar cualquier error y permitir el acceso para que otras capas decidan
            logger.error(f"Error en AdminSecurityMiddleware: {str(e)}", exc_info=True)
            return self.get_response(request)
