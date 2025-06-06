# Documentación Técnica - Sistema de Reserva de Salas

## Índice
1. [Información General](#información-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Requisitos del Sistema](#requisitos-del-sistema)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Estructura de la Base de Datos](#estructura-de-la-base-de-datos)
6. [API y Endpoints](#api-y-endpoints)
7. [Autenticación y Autorización](#autenticación-y-autorización)
8. [Validaciones y Reglas de Negocio](#validaciones-y-reglas-de-negocio)
9. [Logging y Monitoreo](#logging-y-monitoreo)
10. [Seguridad](#seguridad)
11. [Mantenimiento](#mantenimiento)

---

## Información General

### Descripción
Sistema web desarrollado en Django para la gestión y reserva de salas de estudio. Permite a diferentes tipos de usuarios (estudiantes, profesores, administradores) reservar salas según sus permisos y necesidades.

### Tecnologías Utilizadas
- **Backend**: Django 4.2+
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Autenticación**: Sistema integrado de Django
- **Logging**: Python logging module

### Versión
- **Versión Actual**: 1.0
- **Fecha de Última Actualización**: Junio 2025

---

## Arquitectura del Sistema

### Estructura del Proyecto
```
proyecto_calidad/
├── core/                    # Aplicación principal
├── rooms/                   # Gestión de salas y reservas
├── usuarios/                # Gestión de usuarios
├── templates/               # Plantillas HTML
├── static/                  # Archivos estáticos
├── scripts/                 # Scripts de utilidad
└── logs/                    # Archivos de log
```

### Patrón de Arquitectura
- **Patrón MVC**: Modelo-Vista-Controlador implementado con Django
- **Separación de Responsabilidades**: Cada aplicación maneja un dominio específico
- **Middleware Personalizado**: Para logging y manejo de errores

### Flujo de Datos
```
Usuario → Vista → Formulario → Validación → Modelo → Base de Datos
                     ↓
                 Template ← Contexto ← Respuesta
```

---

## Requisitos del Sistema

### Requisitos de Software
- Python 3.8+
- Django 4.2+
- SQLite 3.x (desarrollo) o PostgreSQL 12+ (producción)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

### Requisitos de Hardware (Mínimos)
- **CPU**: 1 GHz
- **RAM**: 2 GB
- **Almacenamiento**: 1 GB disponible
- **Red**: Conexión a internet para dependencias

### Dependencias Python
```
Django==4.2.7
django-crispy-forms==2.0
crispy-bootstrap5==0.7
Pillow==10.0.1
python-decouple==3.8
```

---

## Instalación y Configuración

### 1. Clonación del Proyecto
```bash
git clone https://github.com/Paulobirribarra/proyecto_calidad
cd proyecto_calidad
```

### 2. Entorno Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración de Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Creación de Superusuario
```bash
python manage.py createsuperuser
```

### 6. Carga de Datos Iniciales
```bash
python scripts/setup_db.py
```

### 7. Ejecución del Servidor
```bash
python manage.py runserver
```

---

## Estructura de la Base de Datos

### Modelo de Usuario (usuarios/models.py)
```python
class Usuario:
    - username: CharField (único)
    - email: EmailField
    - first_name: CharField
    - last_name: CharField
    - role: CharField (choices: estudiante, profesor, administrador, soporte)
    - is_active: BooleanField
    - date_joined: DateTimeField
```

### Modelo de Sala (rooms/models.py)
```python
class Room:
    - name: CharField (único)
    - description: TextField
    - capacity: PositiveIntegerField
    - equipment: TextField
    - location: CharField
    - hourly_rate: DecimalField
    - opening_time: TimeField
    - closing_time: TimeField
    - room_type: CharField
    - allowed_roles: JSONField
    - is_active: BooleanField
```

### Modelo de Reserva (rooms/models.py)
```python
class Reservation:
    - user: ForeignKey(Usuario)
    - room: ForeignKey(Room)
    - start_time: DateTimeField
    - end_time: DateTimeField
    - purpose: CharField
    - attendees_count: PositiveIntegerField
    - notes: TextField
    - status: CharField (choices: pending, confirmed, cancelled, completed)
    - created_at: DateTimeField
    - updated_at: DateTimeField
```

### Modelo de Reseña (rooms/models.py)
```python
class Review:
    - reservation: OneToOneField(Reservation)
    - rating: PositiveIntegerField (1-5)
    - cleanliness_rating: PositiveIntegerField (1-5)
    - equipment_rating: PositiveIntegerField (1-5)
    - comfort_rating: PositiveIntegerField (1-5)
    - comment: TextField
    - comment_type: CharField
    - created_at: DateTimeField
```

---

## API y Endpoints

### URLs Principales

#### Autenticación
- `POST /login/` - Inicio de sesión
- `POST /logout/` - Cierre de sesión
- `POST /register/` - Registro de usuario

#### Salas
- `GET /rooms/` - Lista de salas
- `GET /rooms/<id>/` - Detalle de sala
- `POST /rooms/<id>/reserve/` - Reservar sala
- `GET /rooms/search/` - Búsqueda de salas

#### Reservas
- `GET /reservations/` - Lista de reservas del usuario
- `GET /reservations/<id>/` - Detalle de reserva
- `POST /reservations/<id>/cancel/` - Cancelar reserva
- `POST /reservations/<id>/review/` - Calificar reserva

#### Administración
- `GET /admin/rooms/` - Panel de administración
- `POST /admin/rooms/create/` - Crear sala
- `PUT /admin/rooms/<id>/edit/` - Editar sala

### Parámetros de Búsqueda
- `search_query`: Texto de búsqueda en nombre, ubicación o descripción
- `min_capacity`: Capacidad mínima de la sala
- `room_type`: Tipo de sala (sala_estudio, laboratorio, etc.)
- `availability_filter`: Filtro de disponibilidad
- `user_role_filter`: Filtro por rol de usuario

---

## Autenticación y Autorización

### Sistema de Roles
1. **Estudiante**: Puede reservar salas de estudio y salas individuales
2. **Profesor**: Puede reservar todas las salas excepto las de servidor
3. **Administrador**: Acceso completo a todas las funcionalidades
4. **Soporte**: Puede reservar salas técnicas y de laboratorio

### Permisos por Funcionalidad
```python
# Decoradores de seguridad
@login_required          # Requiere autenticación
@user_passes_test(is_admin)  # Solo administradores
@handle_exception        # Manejo de excepciones
```

### Middleware de Seguridad
- **AdminAccessMiddleware**: Controla acceso a URLs administrativas
- **SecurityMiddleware**: Headers de seguridad
- **ExceptionHandlingMiddleware**: Manejo centralizado de errores

---

## Validaciones y Reglas de Negocio

### Validaciones de Formularios

#### Reserva de Sala
- **Fecha/Hora**: No en el pasado, máximo 30 días de anticipación
- **Duración**: Mínimo 1 minuto, máximo 8 horas
- **Asistentes**: Mínimo 1, máximo capacidad de la sala, máximo 4 dígitos (9999)
- **Horario**: Dentro del horario de operación de la sala
- **Disponibilidad**: No conflicto con otras reservas

#### Creación de Sala
- **Nombre**: Único en el sistema
- **Capacidad**: Entre 1 y 100 personas
- **Horarios**: Apertura antes que cierre, entre 6:00 AM y 11:00 PM

### Reglas de Negocio
1. **Cancelación**: Hasta 30 minutos antes del inicio
2. **Solapamiento**: No se permiten reservas solapadas
3. **Actualización de Estado**: Automática al finalizar reservas
4. **Calificación**: Solo para reservas completadas

---

## Logging y Monitoreo

### Configuración de Logs
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
        },
    },
    'loggers': {
        'rooms': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Eventos Registrados
- Inicio/cierre de sesión
- Creación/cancelación de reservas
- Errores de validación
- Intentos de acceso no autorizado
- Operaciones administrativas

### Ubicación de Logs
- **Archivo**: `logs/debug.log`
- **Formato**: `[TIMESTAMP] [LEVEL] [MODULE] MESSAGE`

---

## Seguridad

### Medidas de Seguridad Implementadas

#### Autenticación
- Contraseñas hasheadas con PBKDF2
- Sesiones con timeout automático
- Protección CSRF en formularios

#### Autorización
- Control de acceso basado en roles
- Verificación de permisos en cada vista
- Middleware de seguridad para rutas administrativas

#### Validación de Entrada
- Sanitización de datos de entrada
- Validación del lado servidor
- Protección contra XSS
- Limitación de caracteres en campos numéricos

#### Headers de Seguridad
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

### Configuraciones de Seguridad
```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True  # En producción
SESSION_COOKIE_SECURE = True  # En producción
```

### Accesibilidad Web (WCAG 2.1)

⚠️ **Estado Actual**: **PARCIALMENTE COMPATIBLE**

El sistema implementa algunas características de accesibilidad, pero **NO cumple completamente** con WCAG 2.1 nivel AA.

#### Características Implementadas
- Skip links ("Saltar al contenido principal")
- Estructura semántica HTML5 (`<nav>`, `<main>`, `<section>`)
- Atributos `aria-hidden="true"` en íconos decorativos
- Navegación con `aria-label`
- Breadcrumbs accesibles
- Navegación por teclado básica

#### Problemas Identificados
- **Etiquetado de formularios incompleto**: Faltan `aria-describedby` y instrucciones claras
- **Contraste de colores insuficiente**: Algunos elementos no cumplen ratio 4.5:1
- **Roles ARIA faltantes**: Elementos interactivos sin roles apropiados
- **Textos alternativos**: Íconos y placeholders sin descripciones significativas
- **Indicadores de foco**: Visibilidad insuficiente para navegación por teclado

#### Evaluación Detallada
Ver documento completo: `EVALUACION_ACCESIBILIDAD_WCAG.md`

#### Herramientas de Evaluación Disponibles
```bash
# Herramientas instaladas para evaluación
npm install --save-dev axe-core lighthouse pa11y

# Comandos de evaluación
lighthouse http://localhost:8000 --output html
pa11y http://localhost:8000
```

#### Mejoras Requeridas (Estimado: 3-4 semanas)
1. **Fase 1 (Críticas)**: Etiquetado de formularios, roles ARIA, indicadores de foco
2. **Fase 2 (Importantes)**: Contraste de colores, textos alternativos
3. **Fase 3 (Optimización)**: Pruebas con lectores de pantalla, documentación

---

## Mantenimiento

### Tareas de Mantenimiento Rutinario

#### Diarias
- Verificación de logs de error
- Monitoreo de uso del sistema
- Backup de base de datos

#### Semanales
- Limpieza de sesiones expiradas
- Análisis de patrones de uso
- Verificación de integridad de datos

#### Mensuales
- Actualización de dependencias
- Revisión de logs de seguridad
- Optimización de base de datos

### Scripts de Utilidad
```bash
# Verificar estado de la base de datos
python scripts/check_db.py

# Configurar datos iniciales
python scripts/setup_db.py

# Verificar configuración de tiempo
python scripts/check_time.py
```

### Comandos de Django Útiles
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test

# Shell interactivo
python manage.py shell
```

---

## Resolución de Problemas Comunes

### Error de Migración
```bash
# Resetear migraciones
python manage.py migrate --fake-initial
python manage.py migrate
```

### Error de Permisos
```bash
# Verificar permisos de usuario
python manage.py shell
>>> from usuarios.models import Usuario
>>> user = Usuario.objects.get(username='usuario')
>>> print(user.role)
```

### Error de Base de Datos
```bash
# Verificar conexión
python scripts/check_db.py
```

---

## Contacto y Soporte

Para soporte técnico o consultas sobre el sistema:
- **Email**: soporte@sistema-salas.com
- **Documentación**: Ver MANUAL_USUARIO.md
- **Issues**: Crear ticket en el repositorio

---

*Última actualización: Junio 2025*
