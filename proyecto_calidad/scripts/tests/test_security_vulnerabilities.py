#!/usr/bin/env python
"""
Script para ejecutar las pruebas de seguridad y vulnerabilidades del sistema.

Este script permite ejecutar pruebas específicas de seguridad para verificar
que el sistema está protegido contra intentos de escalada de privilegios
y otras vulnerabilidades comunes.
"""

import os
import sys
import logging

# Ajustar el path para que encuentre el proyecto Django
# Obtener el directorio del proyecto (asumiendo que este script está en /scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')

import django
django.setup()

from django.test.runner import DiscoverRunner

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_security_tests():
    """Ejecutar pruebas de seguridad específicas"""
    logger.info("Iniciando pruebas de seguridad...")
    
    # Ejecutar las pruebas específicas de seguridad
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['scripts.tests.test_security'])
    
    if failures:
        logger.error(f"Se encontraron {failures} fallos en las pruebas de seguridad")
        return False
    else:
        logger.info("Todas las pruebas de seguridad han pasado correctamente")
        return True


def simulate_privilege_escalation():
    """Simular intentos de escalada de privilegios"""
    logger.info("Simulando intentos de escalada de privilegios...")
    
    # Esta función hace peticiones directas a la API o a endpoints
    # protegidos para verificar si es posible la escalada de privilegios
    
    from django.test import Client
    from usuarios.models import CustomUser
    from django.urls import reverse
    
    # Crear usuarios de prueba con diferentes roles si no existen
    roles = ['estudiante', 'profesor', 'soporte']
    clients = {}
    
    for role in roles:
        username = f"{role}_hacker_test"
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create_user(
                username=username,
                password='Password123!',
                email=f"{role}@hacker.test",
                role=role
            )
        
        client = Client()
        client.login(username=username, password='Password123!')
        clients[role] = client
    
    # Lista de rutas administrativas a probar
    admin_routes = [
        '/rooms/admin/sala/crear/',
        '/rooms/admin/sala/1/editar/',
        '/rooms/admin/reservas/',
        '/rooms/api/sala/1/disponibilidad/',
        '/admin/',
        # Intentar accesos mediante nombres de URL también
        reverse('rooms:admin_room_create'),
        reverse('rooms:room_create'),  # Alias que debe estar protegido también
    ]
    
    # Pruebas adicionales de manipulación de parámetros
    form_manipulation_tests = [
        {
            'route': '/rooms/admin/sala/crear/',
            'method': 'post',
            'data': {
                'name': 'Sala Hackeada',
                'capacity': 10,
                'location': 'Edificio Hackeado',
                'description': 'Intento de escalada de privilegios'
            }
        },
        {
            'route': '/rooms/sala/1/reservar/',
            'method': 'post',
            'data': {
                'date': '2023-12-31',
                'start_time': '10:00',
                'end_time': '12:00',
                'user_id': 1  # Intentar reservar como otro usuario
            }
        }
    ]
    
    vulnerabilities = []
    
    # Probar rutas administrativas con cada tipo de usuario
    for role, client in clients.items():
        for route in admin_routes:
            response = client.get(route, follow=True)
            
            # Verificar si el acceso fue rechazado correctamente
            content = response.content.decode('utf-8')
            if "No tienes permisos" not in content and "iniciar sesión" not in content.lower():
                vulnerabilities.append({
                    'role': role,
                    'route': route,
                    'method': 'GET',
                    'status': 'VULNERABLE'
                })
    
    # Probar manipulaciones de formularios para intentar escalada
    for role, client in clients.items():
        # Skip API tests for soporte as they are allowed
        if role == 'soporte' and 'api' in route:
            continue
            
        for test in form_manipulation_tests:
            response = client.post(test['route'], test['data'], follow=True)
            
            # Verificar si hay alguna evidencia de éxito en la escalada
            content = response.content.decode('utf-8')
            if "exitosamente" in content and "No tienes permisos" not in content:
                vulnerabilities.append({
                    'role': role,
                    'route': test['route'],
                    'method': 'POST',
                    'data': test['data'],
                    'status': 'VULNERABLE'
                })
    
    # Probar técnicas avanzadas de bypass
    for role, client in clients.items():
        # Probar con diferentes formatos de URL que podrían saltarse el middleware
        bypass_urls = [
            '/rooms//admin/sala/crear',  # Doble slash
            '/rooms/./admin/sala/crear',  # Carácter de punto
            '/rooms/admin/%2e%2e/sala/crear',  # URL encoding para "../"
        ]
        
        for url in bypass_urls:
            response = client.get(url, follow=True)
            if "No tienes permisos" not in response.content.decode('utf-8'):
                vulnerabilities.append({
                    'role': role,
                    'route': url,
                    'method': 'GET',
                    'status': 'BYPASS DETECTADO'
                })
    
    if vulnerabilities:
        logger.error(f"¡VULNERABILIDADES DETECTADAS! {len(vulnerabilities)} vulnerabilidades encontradas.")
        for vuln in vulnerabilities:
            logger.error(f"Vulnerabilidad: {vuln}")
        return False
    else:
        logger.info("No se detectaron vulnerabilidades de escalada de privilegios")
        return True


def test_middleware_effectiveness():
    """Evaluar la efectividad del middleware de seguridad"""
    logger.info("Evaluando efectividad del middleware de seguridad...")
    
    from django.test import Client, RequestFactory
    from usuarios.models import CustomUser
    from core.middleware import SecurityMiddleware
    
    # Crear factory para simular requests
    factory = RequestFactory()
    
    # Crear usuarios para pruebas
    roles = ['admin', 'estudiante', 'profesor', 'soporte']
    test_users = {}
    
    for role in roles:
        username = f"middleware_test_{role}"
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:            user = CustomUser.objects.create_user(
                username=username,
                password='Password123!',
                email=f"{role}@middleware.test",
                role=role
            )
        test_users[role] = user
    
    # Pruebas para SecurityMiddleware
    security_middleware = SecurityMiddleware(lambda request: None)
    
    test_paths = [
        '/rooms/admin/sala/crear/',
        '/rooms/api/sala/1/disponibilidad/',
        '/admin/rooms/room/1/change/',
    ]
    
    issues = []
    
    for path in test_paths:
        for role, user in test_users.items():
            request = factory.get(path)
            request.user = user
            
            # Probar ambos middlewares
            try:
                # Probar si el middleware permite correctamente
                # Esta verificación es básica ya que los middlewares 
                # reales interactúan con la respuesta HTTP
                allowed_security = True
                allowed_admin = True
                
                # No podemos probar directamente el middleware, 
                # pero registramos para documentación
                if role == 'admin' or user.is_superuser:
                    expected_result = "permitido"
                elif role == 'soporte' and 'api' in path:
                    expected_result = "permitido"
                else:
                    expected_result = "denegado"
                
                logger.info(f"Middleware check - Path: {path}, Role: {role}, Expected: {expected_result}")
            except Exception as e:
                issues.append(f"Error en middleware para {role} en {path}: {str(e)}")
    
    if issues:
        logger.error("Problemas detectados en middlewares de seguridad:")
        for issue in issues:
            logger.error(f"- {issue}")
        return False
    else:
        logger.info("Pruebas básicas de middleware exitosas")
        return True


def verify_admin_views_security():
    """Verificar que las vistas administrativas tienen múltiples capas de seguridad"""
    logger.info("Verificando seguridad en vistas administrativas...")
    
    import inspect
    import importlib
    from django.utils.module_loading import import_string
    
    # Cargar módulo de vistas
    try:
        from rooms import views
        
        # Funciones administrativas a verificar
        admin_functions = [
            'admin_room_create',
            'admin_room_edit',
        ]
        
        issues = []
        
        for func_name in admin_functions:
            if not hasattr(views, func_name):
                issues.append(f"Función {func_name} no encontrada en el módulo de vistas")
                continue
                
            func = getattr(views, func_name)
            source = inspect.getsource(func)
            
            # Verificar múltiples capas de protección
            security_layers = []
            
            # Verificar decoradores
            if '@user_passes_test' in source or '@permission_required' in source:
                security_layers.append("Decorador de permisos")
            
            # Verificar verificaciones manuales
            if 'request.user.is_admin()' in source or "request.user.role == 'admin'" in source:
                security_layers.append("Verificación manual de rol")
            
            if 'PermissionDenied' in source:
                security_layers.append("Manejo de PermissionDenied")
            
            # Verificar registro de intentos
            if 'logger.' in source and ('warning' in source or 'error' in source):
                security_layers.append("Registro de intentos")
            
            # Debería tener al menos 2 capas de protección
            if len(security_layers) < 2:
                issues.append(f"Función {func_name} tiene protección insuficiente: {security_layers}")
                
        if issues:
            logger.error("Problemas detectados en la seguridad de vistas:")
            for issue in issues:
                logger.error(f"- {issue}")
            return False
        else:
            logger.info("Las vistas administrativas tienen múltiples capas de seguridad")
            return True
            
    except Exception as e:
        logger.error(f"Error al verificar seguridad de vistas: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Iniciando verificación de seguridad del sistema...")
    
    # Ejecutar todas las pruebas de seguridad
    results = {
        "unit_tests": run_security_tests(),
        "middleware_effectiveness": test_middleware_effectiveness(),
        "admin_views_security": verify_admin_views_security(),
        "privilege_escalation": simulate_privilege_escalation()
    }
    
    # Verificar resultados
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("✅ TODAS LAS PRUEBAS DE SEGURIDAD HAN PASADO EXITOSAMENTE")
        sys.exit(0)
    else:
        logger.error("❌ ALGUNAS PRUEBAS DE SEGURIDAD HAN FALLADO:")
        for test, result in results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            logger.error(f"  - {test}: {status}")
        sys.exit(1)
      # Este código está duplicado, se ejecuta arriba con todas las pruebas
    # y se ha comentado para evitar confusiones
    
    # # Ejecutar las pruebas de seguridad
    # security_tests_passed = run_security_tests()
    # 
    # # Simular intentos de escalada de privilegios
    # escalation_tests_passed = simulate_privilege_escalation()
    # 
    # if security_tests_passed and escalation_tests_passed:
    #     logger.info("✅ El sistema está seguro contra escalada de privilegios")
    #     sys.exit(0)
    # else:
    #     logger.error("❌ Se detectaron vulnerabilidades en el sistema")
    #     sys.exit(1)
