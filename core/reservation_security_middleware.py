"""
Middleware de Seguridad para Reservas

Este middleware intercepta las requests relacionadas con reservas
y aplica medidas de seguridad automáticamente antes de procesar
las solicitudes.
"""

from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging
import json

logger = logging.getLogger(__name__)


class ReservationSecurityMiddleware(MiddlewareMixin):
    """
    Middleware para aplicar controles de seguridad en reservas.
    
    Intercepta requests de reserva y aplica:
    - Rate limiting
    - Detección de comportamiento abusivo
    - Bloqueos temporales
    - Logging de seguridad
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que requieren controles de seguridad
        self.protected_urls = [
            '/rooms/reserve/',
            '/rooms/api/reserve/',
            '/api/rooms/reserve/'
        ]
        super().__init__(get_response)
    
    def process_request(self, request):
        """Procesar request antes de que llegue a la vista."""
        # Solo aplicar a usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Solo aplicar a URLs de reserva
        if not any(url in request.path for url in self.protected_urls):
            return None
        
        # Solo aplicar a métodos POST (creación de reservas)
        if request.method != 'POST':
            return None
        
        # Exemp tar administradores si tienen permisos especiales
        if request.user.is_superuser:
            return None
        
        try:
            from core.reservation_security import SecurityManager
            
            # Verificar si el usuario está bloqueado
            is_blocked, blocked_until = SecurityManager.is_user_blocked(request.user)
            
            if is_blocked:
                logger.warning(
                    f"Usuario bloqueado {request.user.username} intentó hacer reserva "
                    f"desde IP {request.META.get('REMOTE_ADDR', 'unknown')}"
                )
                
                # Registrar el intento
                SecurityManager.log_action(
                    user=request.user,
                    action='attempt_blocked',
                    room_name="unknown",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    additional_data={
                        'reason': 'user_temporarily_blocked',
                        'blocked_until': blocked_until.isoformat() if blocked_until else None,
                        'url': request.path
                    }
                )
                
                # Respuesta según el tipo de request
                if request.headers.get('Accept', '').startswith('application/json'):
                    return JsonResponse({
                        'error': True,
                        'message': f'Tu cuenta está temporalmente bloqueada hasta las {blocked_until.strftime("%H:%M")} por comportamiento abusivo.',
                        'blocked_until': blocked_until.isoformat(),
                        'type': 'user_blocked'
                    }, status=429)
                else:
                    messages.error(
                        request,
                        f'Tu cuenta está temporalmente bloqueada hasta las {blocked_until.strftime("%H:%M")} '
                        f'por comportamiento abusivo. Intenta más tarde.'
                    )
                    return redirect('rooms:room_list')
            
            # Verificar límites básicos de rate limiting
            rate_allowed, violations, warnings = SecurityManager.check_rate_limits(request.user)
            
            if not rate_allowed:
                # Determinar el tipo de violación más grave
                violation_types = [v['type'] for v in violations]
                
                main_violation = violations[0]  # Tomar la primera violación
                
                logger.warning(
                    f"Rate limit excedido para usuario {request.user.username}: "
                    f"{', '.join(violation_types)}"
                )
                
                # Registrar la violación
                SecurityManager.log_action(
                    user=request.user,
                    action='attempt_blocked',
                    room_name="unknown",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    additional_data={
                        'reason': 'rate_limit_exceeded',
                        'violations': violation_types,
                        'url': request.path
                    }
                )
                
                # Respuesta según el tipo de request
                if request.headers.get('Accept', '').startswith('application/json'):
                    return JsonResponse({
                        'error': True,
                        'message': main_violation['message'],
                        'violations': violations,
                        'type': 'rate_limit_exceeded'
                    }, status=429)
                else:
                    messages.error(request, f"Límite de reservas excedido: {main_violation['message']}")
                    return redirect('rooms:room_list')
            
            # Si hay advertencias, mostrarlas pero permitir continuar
            if warnings:
                for warning in warnings:
                    if request.headers.get('Accept', '').startswith('application/json'):
                        # Para requests AJAX, agregar las advertencias al contexto
                        if not hasattr(request, '_reservation_warnings'):
                            request._reservation_warnings = []
                        request._reservation_warnings.append(warning)
                    else:
                        messages.warning(request, f"Advertencia: {warning['message']}")
        
        except Exception as e:
            logger.error(f"Error en ReservationSecurityMiddleware: {e}", exc_info=True)
            # En caso de error, permitir continuar pero registrar el problema
        
        return None
    
    def process_response(self, request, response):
        """Procesar respuesta después de la vista."""
        # Solo procesar para usuarios autenticados y URLs protegidas
        if (not request.user.is_authenticated or 
            not any(url in request.path for url in self.protected_urls)):
            return response
        
        # Si la respuesta fue exitosa (nueva reserva creada), registrar la acción
        if (request.method == 'POST' and 
            response.status_code in [200, 201, 302] and  # Incluir redirects
            hasattr(request, 'resolver_match')):
            
            try:
                from core.reservation_security import SecurityManager
                
                # Intentar extraer información de la sala de diferentes fuentes
                room_name = "unknown"
                reservation_id = None
                
                # Si es un redirect a reservation_detail, extraer el ID
                if response.status_code == 302 and 'reservation_detail' in response.get('Location', ''):
                    try:
                        import re
                        match = re.search(r'/reservation/(\d+)/', response.get('Location', ''))
                        if match:
                            reservation_id = int(match.group(1))
                    except:
                        pass
                
                # Intentar obtener el nombre de la sala desde el POST data
                if hasattr(request, 'POST'):
                    room_id = request.POST.get('room')
                    if room_id:
                        try:
                            from rooms.models import Room
                            room = Room.objects.get(id=room_id)
                            room_name = room.name
                        except:
                            pass
                
                # Registrar la acción exitosa
                SecurityManager.log_action(
                    user=request.user,
                    action='create',
                    room_name=room_name,
                    reservation_id=reservation_id,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    additional_data={
                        'url': request.path,
                        'response_status': response.status_code
                    }
                )
                
            except Exception as e:
                logger.error(f"Error registrando acción exitosa: {e}")
        
        # Agregar advertencias a respuestas JSON si existen
        if (hasattr(request, '_reservation_warnings') and 
            response.status_code == 200 and
            response.get('Content-Type', '').startswith('application/json')):
            
            try:
                import json
                data = json.loads(response.content.decode('utf-8'))
                data['warnings'] = request._reservation_warnings
                response.content = json.dumps(data).encode('utf-8')
            except:
                pass
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware adicional para rate limiting general basado en IP.
    
    Proporciona una capa adicional de protección contra ataques
    automatizados desde la misma IP.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Aplicar rate limiting por IP para ciertas rutas."""
        # Rutas que requieren rate limiting por IP
        rate_limited_paths = [
            '/rooms/reserve/',
            '/accounts/login/',
            '/accounts/register/',
        ]
        
        if not any(path in request.path for path in rate_limited_paths):
            return None
        
        # Obtener IP del cliente
        ip_address = self.get_client_ip(request)
        
        # Aplicar rate limiting
        if not self.check_rate_limit(ip_address, request.path):
            logger.warning(f"Rate limit por IP excedido: {ip_address} en {request.path}")
            
            if request.headers.get('Accept', '').startswith('application/json'):
                return JsonResponse({
                    'error': True,
                    'message': 'Demasiadas solicitudes. Intenta de nuevo en unos minutos.',
                    'type': 'ip_rate_limit'
                }, status=429)
            else:
                messages.error(
                    request,
                    'Demasiadas solicitudes desde tu conexión. Intenta de nuevo en unos minutos.'
                )
                return redirect('rooms:room_list')
        
        return None
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_rate_limit(self, ip_address, path):
        """
        Verificar rate limit por IP.
        
        Límites:
        - Reservas: 10 por hora por IP
        - Login: 20 por hora por IP
        - Registro: 5 por hora por IP
        """
        # Configurar límites según el path
        if 'reserve' in path:
            limit = 10
            window = 3600  # 1 hora
        elif 'login' in path:
            limit = 20
            window = 3600
        elif 'register' in path:
            limit = 5
            window = 3600
        else:
            return True  # Sin límite para otras rutas
        
        # Crear clave de cache
        cache_key = f"ip_rate_limit_{ip_address}_{path.replace('/', '_')}"
        
        # Obtener contador actual
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return False
        
        # Incrementar contador
        cache.set(cache_key, current_count + 1, timeout=window)
        
        return True
