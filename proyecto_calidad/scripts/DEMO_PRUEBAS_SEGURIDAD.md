# Guía de Demostración de Pruebas de Seguridad

Esta guía te permitirá realizar una demostración en vivo de las pruebas de seguridad implementadas para los formularios de login y registro.

## Preparación

1. Abre dos ventanas de terminal:
   - Una para ejecutar los comandos
   - Otra para mostrar el código mientras explicas

2. Asegúrate de estar en el directorio raíz del proyecto:
   ```
   cd e:\Desktop\Final_QA\proyecto_calidad
   ```

## Demostración 1: Ejecutar la Suite Completa de Pruebas

### Paso 1: Mostrar el archivo de pruebas
Muestra el archivo de pruebas de seguridad para explicar qué se va a probar:

```
code scripts/tests/test_forms_security.py
```

Puedes destacar:
- Los diferentes tipos de pruebas (SQL injection, XSS, etc.)
- Los patrones de inyección que se utilizarán
- La configuración de los usuarios de prueba

### Paso 2: Ejecutar todas las pruebas de seguridad

```
python manage.py test scripts.tests.test_forms_security
```

Esto ejecutará las 7 pruebas y mostrará los resultados. Destaca los mensajes de advertencia que confirman que el sistema rechaza correctamente los intentos maliciosos.

## Demostración 2: Pruebas Individuales

Para una demostración más detallada, puedes ejecutar pruebas específicas:

### Prueba de Inyección SQL

```
python manage.py test scripts.tests.test_forms_security.FormSecurityTest.test_login_form_sql_injection
```

Explica cómo Django utiliza ORM y consultas parametrizadas para prevenir inyecciones SQL.

### Prueba XSS

```
python manage.py test scripts.tests.test_forms_security.FormSecurityTest.test_login_form_xss
```

Muestra cómo Django escapa automáticamente los caracteres HTML peligrosos en las plantillas.

### Prueba de Inyección de Plantillas

```
python manage.py test scripts.tests.test_forms_security.FormSecurityTest.test_template_injection
```

Explica cómo el sistema de plantillas de Django no interpreta el código de plantilla en entradas de usuario.

### Prueba de Almacenamiento de Contraseñas

```
python manage.py test scripts.tests.test_forms_security.FormSecurityTest.test_secure_password_storage
```

Demuestra que las contraseñas no se almacenan en texto plano sino con hash.

## Demostración 3: Prueba Manual de Seguridad

Para una demostración más visual:

### Paso 1: Inicia el servidor de desarrollo

```
python manage.py runserver
```

### Paso 2: Abre el navegador y accede a los formularios

- Accede a http://127.0.0.1:8000/usuarios/login/
- Intenta un ataque XSS básico escribiendo `<script>alert('XSS')</script>` en el campo de usuario
- Muestra que el código se muestra como texto, no se ejecuta

### Paso 3: Intenta una inyección SQL

- En el formulario de login, intenta: `' OR 1=1 --` como nombre de usuario y contraseña
- Muestra que el sistema rechaza el intento de login

## Demostración 4: Verificación de CSRF

### Paso 1: Usar las herramientas de desarrollo del navegador

- Abre las herramientas de desarrollo (F12) en el formulario de login
- Muestra el token CSRF en el HTML del formulario
- Explica cómo esto protege contra ataques CSRF

### Paso 2: Demuestra la protección contra CSRF

- Intenta enviar el formulario con curl sin el token CSRF
  ```
  curl -X POST http://127.0.0.1:8000/usuarios/login/ -d "username=admin_test&password=Password123"
  ```
- Muestra el código 403 (Forbidden) que recibe

## Demostración 5: Protección contra Escalada de Privilegios

### Paso 1: Crea un usuario normal

- Registra un nuevo usuario en http://127.0.0.1:8000/usuarios/register/
- Muestra que se crea con rol de estudiante

### Paso 2: Examina la base de datos

- Muestra que los campos de privilegios no se pueden manipular desde el formulario:
  ```
  python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.last().is_staff, User.objects.last().is_superuser, User.objects.last().role)"
  ```

## Tips para la Presentación

1. **Prepara el código de antemano**: Ten el archivo test_forms_security.py abierto.
2. **Habla sobre las buenas prácticas**: Mientras se ejecutan las pruebas, explica las buenas prácticas de seguridad implementadas.
3. **Muestra el informe**: Al final, abre el archivo SECURITY_TEST_RESULTS.md para mostrar el resumen de resultados.
4. **Destaca la importancia**: Explica por qué estas pruebas son cruciales para la seguridad de la aplicación.
5. **Controla el tiempo**: Cada demostración debería tomar aproximadamente 2-3 minutos.

## Material Visual Adicional

También puedes crear una diapositiva que resuma las vulnerabilidades probadas:

| Tipo de Vulnerabilidad | Estatus | Método de Protección |
|----------------------|---------|---------------------|
| Inyección SQL        | ✅ Protegido | ORM de Django       |
| XSS                  | ✅ Protegido | Auto-escapado       |
| CSRF                 | ✅ Protegido | Tokens CSRF         |
| Inyección Templates  | ✅ Protegido | Escapado seguro     |
| Escalada Privilegios | ✅ Protegido | Validación servidor |
| Contraseñas Débiles  | ✅ Protegido | Validación compleja |
| Almacenamiento       | ✅ Protegido | Hash PBKDF2         |
