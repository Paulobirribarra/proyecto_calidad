"""
Tests para verificar la seguridad del sistema contra escalada de privilegios.

Este archivo contiene pruebas que simulan intentos de acceso a rutas
administrativas por usuarios con roles estándar para asegurar que
el sistema detecte y bloquee estos intentos.
"""

import unittest
from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import CustomUser


class SecurityTests(TestCase):
    """Pruebas para validar la seguridad del sistema"""

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuarios con diferentes roles
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test',
            password='Password123!',
            email='admin@test.com',
            role='admin'
        )
        
        self.profesor_user = CustomUser.objects.create_user(
            username='profesor_test',
            password='Password123!',
            email='profesor@test.com',
            role='profesor'
        )
        
        self.estudiante_user = CustomUser.objects.create_user(
            username='estudiante_test',
            password='Password123!',
            email='estudiante@test.com',
            role='estudiante'
        )
        
        self.soporte_user = CustomUser.objects.create_user(
            username='soporte_test',
            password='Password123!',
            email='soporte@test.com',
            role='soporte'
        )
        
        # Crear clientes HTTP para cada tipo de usuario
        self.admin_client = Client()
        self.profesor_client = Client()
        self.estudiante_client = Client()
        self.soporte_client = Client()
        self.anonymous_client = Client()
        
        # Iniciar sesión con cada cliente
        self.admin_client.login(username='admin_test', password='Password123!')
        self.profesor_client.login(username='profesor_test', password='Password123!')
        self.estudiante_client.login(username='estudiante_test', password='Password123!')
        self.soporte_client.login(username='soporte_test', password='Password123!')

    def test_admin_access(self):
        """Probar que los administradores pueden acceder a rutas administrativas"""
        response = self.admin_client.get(reverse('rooms:admin_room_create'))
        self.assertNotEqual(response.status_code, 302)  # No debería redirigir
        
        response = self.admin_client.get(reverse('rooms:admin_room_edit', args=[1]), follow=True)
        # Puede redirigir si la sala no existe, pero no por permisos
        self.assertNotContains(response, "No tienes permisos")

    def test_unauthorized_admin_access(self):
        """Probar que los no-administradores son redirigidos desde rutas administrativas"""
        # Profesor intentando acceder
        response = self.profesor_client.get(reverse('rooms:admin_room_create'), follow=True)
        self.assertContains(response, "administradores")
        
        # Estudiante intentando acceder
        response = self.estudiante_client.get(reverse('rooms:admin_room_create'), follow=True)
        self.assertContains(response, "administradores")
        
        # Soporte intentando acceder
        response = self.soporte_client.get(reverse('rooms:admin_room_create'), follow=True)
        self.assertContains(response, "administradores")
        
        # Usuario anónimo intentando acceder
        response = self.anonymous_client.get(reverse('rooms:admin_room_create'), follow=True)
        self.assertRedirects(response, '/usuarios/login/?next=/rooms/admin/sala/crear/')

    def test_api_access(self):
        """Probar el acceso a endpoints de API según roles"""
        # Administrador y soporte deberían tener acceso
        response = self.admin_client.get(reverse('rooms:api_room_availability', args=[1]), follow=True)
        # Si hay un error, debería ser por otra razón, no por permisos
        self.assertNotContains(response, "permisos")
        
        response = self.soporte_client.get(reverse('rooms:api_room_availability', args=[1]), follow=True)
        self.assertNotContains(response, "permisos")
        
        # Estudiantes y profesores no deberían tener acceso
        response = self.estudiante_client.get(reverse('rooms:api_room_availability', args=[1]), follow=True)
        self.assertContains(response, "permisos")
        response = self.profesor_client.get(reverse('rooms:api_room_availability', args=[1]), follow=True)
        self.assertContains(response, "No tienes permisos")
        
    def test_url_tampering(self):
        """Probar que modificar URLs manualmente no permite escalada de privilegios"""
        # Estudiante intentando acceder a una URL administrativa no registrada
        response = self.estudiante_client.get('/rooms/admin/sala/gestionar/', follow=True)
        self.assertContains(response, "administradores")
        
        # Profesor intentando acceder mediante una URL alternativa
        response = self.profesor_client.get('/rooms/admin/crear-sala/', follow=True)
        # Debería ser 404 o redirigir con mensaje de error
        self.assertTrue(response.status_code in [404, 302])


if __name__ == '__main__':
    unittest.main()
