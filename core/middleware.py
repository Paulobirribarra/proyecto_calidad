"""
Middleware personalizado para seguridad adicional del sistema.

Este middleware refuerza el control de acceso basado en roles para
determinadas URLs, evitando la escalada de privilegios.
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from django.http import Http404
import re
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    Middleware que mejora la seguridad verificando permisos basados en patrones de URL.
    
    Este middleware complementa los decoradores de vistas al añadir una capa adicional
    de seguridad que verifica los roles de usuario basado en patrones de URL.
    Incluye protección reforzada para rutas administrativas.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Definir URLs protegidas con expresiones regulares y roles permitidos
        self.protected_paths = [
            # Formato: (regex_pattern, [roles_permitidos], mensaje_rechazo, es_ruta_admin)
            (r'^/rooms/admin/', ['admin'], "Acceso denegado.", True),
            (r'^/rooms/api/', ['admin', 'soporte'], "Acceso denegado.", False),
            (r'.*/admin/.*', ['admin'], "Acceso denegado.", True),
            (r'^/admin/', ['admin'], "Acceso denegado.", True),
            # Protección contra técnicas de bypass
            (r'^/rooms//+admin/', ['admin'], "Acceso denegado.", True),
            (r'^/rooms/\./admin/', ['admin'], "Acceso denegado.", True),
        ]
        # Compilar las expresiones regulares para mejor rendimiento
        self.compiled_patterns = [(re.compile(pattern), roles, message, is_admin) 
                                for pattern, roles, message, is_admin in self.protected_paths]
    def get_client_ip(self, request):
        """Obtener la IP real del cliente, considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
                                
    def __call__(self, request):
        try:
            # Verificar si la ruta actual está protegida
            path = request.path  # Usar path en vez de full_path para excluir parámetros query
            
            # Detectar intentos de acceso a rutas administrativas mal escritas (fuzzing)
            admin_variations = [
                'admin', 'admin/', 'Admin', 'ADMIN', 'administrator', 'admin.php',
                'ademin', 'admon', 'admn', 'adm', 'administracion', 'panel'
            ]
            
            # Verificar si la URL parece un intento de descubrir rutas admin
            path_clean = path.strip('/')
            if path_clean.lower() in [var.lower() for var in admin_variations] and path_clean != 'admin':
                logger.warning(f"¡Posible intento de fuzzing admin detectado! URL: {path} desde IP: {self.get_client_ip(request)}")
                # Redirigir sin revelar información
                raise Http404("Página no encontrada")
            
            # Detectar si hay algún intento de manipulación de URL (técnicas bypass)
            if '//' in path or '/./' in path or '/../' in path or '%2e' in path.lower():
                logger.warning(f"¡Posible intento de bypass de seguridad detectado! URL: {path}")
                raise Http404("Página no encontrada")
            
            # Si el usuario no está autenticado y trata de acceder a ruta protegida, redirigir al login
            if not request.user.is_authenticated:
                for pattern, _, _, _ in self.compiled_patterns:
                    if pattern.match(path):
                        from django.conf import settings
                        login_url = settings.LOGIN_URL
                        return redirect(f"{login_url}?next={request.path}")
            
            # Si el usuario está autenticado, verificar permisos
            elif request.user.is_authenticated:
                # Los superusuarios tienen acceso completo
                if request.user.is_superuser:
                    return self.get_response(request)
                    
                # Comprobar si la URL actual coincide con algún patrón protegido
                for pattern, allowed_roles, error_message, is_admin_route in self.compiled_patterns:
                    if pattern.match(path):
                        # Verificar si el usuario tiene el rol adecuado
                        user_role = request.user.role
                        
                        # Protección reforzada para rutas administrativas
                        if is_admin_route:
                            # Verificar si es admin de múltiples maneras para mayor seguridad
                            is_admin = (
                                user_role == 'admin' or 
                                (hasattr(request.user, 'is_admin') and request.user.is_admin()) or
                                request.user.is_staff
                            )
                            if not is_admin:
                                # Registrar intento de acceso no autorizado a ruta admin
                                logger.warning(
                                    f"¡ALERTA DE SEGURIDAD! Intento de acceso a ruta ADMIN: "
                                    f"Usuario {request.user.username} con rol '{user_role}' intentó acceder a {path}"
                                )
                                # No mostrar mensaje para evitar revelar información sensible
                                return redirect('rooms:room_list')
                        
                        # Para rutas no administrativas, verificar roles permitidos normalmente
                        elif user_role not in allowed_roles:
                            # Registrar intento de acceso no autorizado
                            logger.warning(
                                f"Intento de acceso no autorizado: Usuario {request.user.username} "
                                f"con rol '{user_role}' intentó acceder a {path}"
                            )
                            # No mostrar mensaje para evitar revelar información sensible
                            return redirect('rooms:room_list')
            
            # Continuar con el flujo normal de la solicitud
            response = self.get_response(request)
            return response
            
        except Http404:
            # Re-lanzar Http404 para que sea manejado por Django
            raise
        except Exception as e:
            # Registrar cualquier error inesperado y permitir el acceso normal
            # (seguridad en profundidad: otras capas pueden bloquear acceso)
            logger.error(f"Error en SecurityMiddleware: {str(e)}", exc_info=True)
            return self.get_response(request)
