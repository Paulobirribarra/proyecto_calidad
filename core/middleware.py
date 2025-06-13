from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from django.http import Http404
import re
import logging
from django.conf import settings 

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
            (r'^/rooms/admin/', ['admin'], "Acceso denegado.", True),
            (r'^/rooms/api/', ['admin', 'soporte'], "Acceso denegado.", False),
            (r'.*/admin/.*', ['admin'], "Acceso denegado.", True),
            (r'^/admin/', ['admin'], "Acceso denegado.", True),
            (r'^/rooms//+admin/', ['admin'], "Acceso denegado.", True),
            (r'^/rooms/\./admin/', ['admin'], "Acceso denegado.", True),
        ]
        # Compilar las expresiones regulares para mejor rendimiento
        self.compiled_patterns = [(re.compile(pattern), roles, message, is_admin) 
                                for pattern, roles, message, is_admin in self.protected_paths]
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente, considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
                                
    def __call__(self, request):
        try:
            # Verificar si la sesión está marcada como cerrada
            if request.session.get('is_logged_out', False):
                last_username = request.session.get('last_username', 'desconocido')
                ip_address = self.get_client_ip(request)
                logger.warning(
                    f"[SEGURIDAD] ALERTA: Intento de acceso con sesión cerrada detectado: "
                    f"Usuario '{last_username}' desde IP {ip_address}. "
                    f"Posible uso del botón 'atrás' después de cerrar sesión. "
                    f"URL solicitada: {request.path} [Demostración de Seguridad]"
                )
                request.session.flush()
                messages.warning(
                    request,
                    "¡Sesión cerrada detectada! Por seguridad, se ha bloqueado el acceso. "
                    "Inicia sesión nuevamente para continuar. [Demostración de Seguridad]"
                )
                return redirect(settings.LOGIN_URL)
            
            # Verificar si la ruta actual está protegida
            path = request.path
            
            # Detectar intentos de acceso a rutas administrativas mal escritas (fuzzing)
            admin_variations = [
                'admin', 'admin/', 'Admin', 'ADMIN', 'administrator', 'admin.php',
                'ademin', 'admon', 'admn', 'adm', 'administracion', 'panel'
            ]
            
            path_clean = path.strip('/')
            if path_clean.lower() in [var.lower() for var in admin_variations] and path_clean != 'admin':
                logger.warning(
                    f"[SEGURIDAD] ALERTA: Posible intento de fuzzing admin detectado! "
                    f"URL: {path} desde IP: {self.get_client_ip(request)} [Demostración de Seguridad]"
                )
                raise Http404("Página no encontrada")
            
            # Detectar intentos de manipulación de URL (técnicas bypass)
            if '//' in path or '/./' in path or '/../' in path or '%2e' in path.lower():
                logger.warning(
                    f"[SEGURIDAD] ALERTA: Posible intento de bypass de seguridad detectado! "
                    f"URL: {path} desde IP: {self.get_client_ip(request)} [Demostración de Seguridad]"
                )
                raise Http404("Página no encontrada")
            
            # Si el usuario no está autenticado y trata de acceder a ruta protegida, redirigir al login
            if not request.user.is_authenticated:
                for pattern, _, _, _ in self.compiled_patterns:
                    if pattern.match(path):
                        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            
            # Si el usuario está autenticado, verificar permisos
            elif request.user.is_authenticated:
                # Los superusuarios tienen acceso completo
                if request.user.is_superuser:
                    return self.get_response(request)
                    
                # Comprobar si la URL actual coincide con algún patrón protegido
                for pattern, allowed_roles, error_message, is_admin_route in self.compiled_patterns:
                    if pattern.match(path):
                        # Verificar si el usuario tiene el rol adecuado
                        user_role = getattr(request.user, 'role', 'desconocido')
                        
                        # Protección reforzada para rutas administrativas
                        if is_admin_route:
                            is_admin = (
                                user_role == 'admin' or 
                                (hasattr(request.user, 'is_admin') and request.user.is_admin) or
                                request.user.is_staff
                            )
                            if not is_admin:
                                logger.warning(
                                    f"[SEGURIDAD] ALERTA: Intento de acceso no autorizado a ruta ADMIN: "
                                    f"Usuario {request.user.username} con rol '{user_role}' intentó acceder a {path} "
                                    f"[Demostración de Seguridad]"
                                )
                                return redirect('rooms:room_list')
                        
                        # Para rutas no administrativas, verificar roles permitidos
                        elif user_role not in allowed_roles:
                            logger.warning(
                                f"[SEGURIDAD] ALERTA: Intento de acceso no autorizado: "
                                f"Usuario {request.user.username} con rol '{user_role}' intentó acceder a {path} "
                                f"[Demostración de Seguridad]"
                            )
                            return redirect('rooms:room_list')
            
            # Continuar con el flujo normal de la solicitud
            return self.get_response(request)
            
        except Http404:
            raise
        except Exception as e:
            logger.error(f"[SEGURIDAD] Error en SecurityMiddleware: {str(e)}", exc_info=True)
            return self.get_response(request)