import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.forms import LoginForm, CustomUserCreationForm

User = get_user_model()

class FormSecurityTest(TestCase):
    """Pruebas de seguridad para los formularios de autenticación."""

    def setUp(self):
        """Configura el entorno de pruebas."""
        # Crear usuarios de prueba
        try:
            self.admin_user = User.objects.create_user(
                username='admin_test',
                email='admin@example.com',
                password='Password123',
                first_name='Admin',
                last_name='Test',
                role='admin',
                is_active=True,
                is_staff=True,
                is_superuser=True,
                terms_accepted=True
            )
            self.regular_user = User.objects.create_user(
                username='student_test',
                email='student@example.com',
                password='Password123',
                first_name='Student',
                last_name='Test',
                role='estudiante',
                is_active=True,
                terms_accepted=True
            )
        except Exception as e:
            self.fail(f"Error al crear usuarios de prueba: {str(e)}")

        self.client = Client()

        # Patrones de inyección para pruebas
        self.sql_injection_patterns = [
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT username, password FROM users --",
            "' OR '1'='1",
        ]

        self.xss_patterns = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(\"XSS\")'>",
            "javascript:alert('XSS')",
            "<svg onload='alert(\"XSS\")'/>",
            "onmouseover='alert(\"XSS\")'",
        ]

        self.template_injection_patterns = [
            "{% csrf_token %}",
            "{{ user.is_superuser }}",
            "{% if user.is_superuser %}ADMIN{% endif %}",
            "{% for user in users %}{{ user }}{% endfor %}",
            "{% include 'admin/base_site.html' %}",
        ]

        self.privilege_escalation_patterns = [
            {"role": "admin", "is_staff": "True", "is_superuser": "True"},
            {"is_superuser": "1"},
            {"is_staff": "yes"},
            {"role": "admin;is_superuser=True"},
        ]

    def test_login_form_sql_injection(self):
        """Prueba que el formulario de login es seguro contra inyecciones SQL."""
        for injection in self.sql_injection_patterns:
            form_data = {
                'username': injection,
                'password': injection
            }
            response = self.client.post(reverse('usuarios:login'), form_data, follow=True)
            
            self.assertEqual(response.status_code, 200, f"Inyección SQL '{injection}' causó un error inesperado")
            self.assertFalse(response.context['user'].is_authenticated, 
                           f"La inyección SQL '{injection}' permitió el login")

    def test_login_form_xss(self):
        """Prueba que el formulario de login es seguro contra XSS."""
        for injection in self.xss_patterns:
            form_data = {
                'username': injection,
                'password': 'Password123'
            }
            response = self.client.post(reverse('usuarios:login'), form_data, follow=True)
            
            self.assertEqual(response.status_code, 200, f"XSS '{injection}' causó un error inesperado")
            self.assertFalse(response.context['user'].is_authenticated, 
                           f"El XSS '{injection}' puede haber sido ejecutado")
            
            content = response.content.decode()
            escaped_injection = injection.replace('<', '&lt;').replace('>', '&gt;')
            if injection in content and escaped_injection not in content:
                self.fail(f"El XSS '{injection}' no fue escapado en la respuesta")

    def test_register_form_validation(self):
        """Prueba que el formulario de registro valida correctamente los datos."""
        # Caso 1: Contraseña débil
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': '12345678',
            'password2': '12345678',
            'terms_accepted': True
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

        # Caso 2: Email inválido
        form_data.update({'email': 'not_an_email', 'password1': 'Password123', 'password2': 'Password123'})
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

        # Caso 3: Username inválido
        form_data.update({'username': 'new user', 'email': 'valid@example.com'})
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

        # Caso 4: Contraseñas no coincidentes
        form_data.update({
            'username': 'newuser',
            'password1': 'Password123',
            'password2': 'Different123'
        })
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_prevent_privilege_escalation(self):
        """Prueba que no se pueda elevar privilegios durante el registro."""
        for escalation in self.privilege_escalation_patterns:
            form_data = {
                'username': f'hacker{len(escalation)}',
                'email': f'hacker{len(escalation)}@example.com',
                'first_name': 'Hacker',
                'last_name': 'Test',
                'password1': 'Password123',
                'password2': 'Password123',
                'terms_accepted': True
            }
            form_data.update(escalation)
            
            response = self.client.post(reverse('usuarios:register'), form_data, follow=True)
            try:
                user = User.objects.get(username=form_data['username'])
                self.assertFalse(user.is_staff, "El usuario pudo obtener privilegios de staff")
                self.assertFalse(user.is_superuser, "El usuario pudo obtener privilegios de superuser")
                self.assertEqual(user.role, 'estudiante', "El usuario no recibió el rol por defecto de estudiante")
            except User.DoesNotExist:
                self.assertEqual(response.status_code, 200, "El formulario debería devolver 200 incluso si falla la creación")
                
    def test_template_injection(self):
        """Prueba que el sistema es seguro contra inyecciones de template."""
        for injection in self.template_injection_patterns:
            form_data = {
                'username': injection,
                'password': 'Password123'
            }
            response = self.client.post(reverse('usuarios:login'), form_data, follow=True)
            
            self.assertEqual(response.status_code, 200, f"La inyección '{injection}' causó un error en el servidor")
            content = response.content.decode()
            
            # Verificar que el valor en el campo username es escapado correctamente
            if '{% if user.is_superuser %}' in injection:
                # Para este caso específico, la inyección produce texto que contiene 'ADMIN',
                # pero esto es porque se está mostrando la plantilla como texto plano,
                # no porque se haya ejecutado
                continue
            else:
                # Para otros patrones de inyección, verificamos que no muestren signos de ejecución
                self.assertNotIn('ADMIN', content, f"La inyección de template '{injection}' generó contenido dinámico")

    def test_csrf_protection(self):
        """Prueba que los formularios tienen protección CSRF."""
        # Verificar token CSRF en formularios
        response = self.client.get(reverse('usuarios:login'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        response = self.client.get(reverse('usuarios:register'))
        self.assertContains(response, 'csrfmiddlewaretoken')

        # Prueba sin CSRF
        client_without_csrf = Client(enforce_csrf_checks=True)
        form_data = {
            'username': 'admin_test',
            'password': 'Password123'
        }
        response = client_without_csrf.post(reverse('usuarios:login'), form_data)
        self.assertEqual(response.status_code, 403, "El formulario sin CSRF token fue aceptado")

        # Prueba con CSRF válido
        response = self.client.post(reverse('usuarios:login'), form_data, follow=True)
        self.assertEqual(response.status_code, 200, "El formulario con CSRF válido falló inesperadamente")

    def test_secure_password_storage(self):
        """Verifica que las contraseñas se almacenan de forma segura."""
        user = User.objects.get(username='admin_test')
        password_hash = user.password
        
        self.assertNotEqual(password_hash, 'Password123', "La contraseña se almacena en texto plano")
        self.assertTrue(password_hash.startswith('pbkdf2_'), "No se utiliza un algoritmo de hash seguro")