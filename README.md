# 🏢 Sistema de Gestión de Salas de Estudio Inteligentes

Sistema web desarrollado en Django para la gestión inteligente de reservas de salas de estudio. Permite a los usuarios buscar, reservar y calificar salas de estudio con funcionalidades avanzadas de autenticación, roles y administración.

## 🚀 Inicio Rápido

### 1. Prerrequisitos
- Python 3.8+
- Git

### 2. Instalación
```bash
# Clonar el repositorio
git clone <repository-url>
cd Final_QA

# Crear y activar entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
cd proyecto_calidad
pip install -r requirements.txt
```

### 3. Configuración Inicial
```bash
# Aplicar migraciones de base de datos
python manage.py migrate

# Poblar con datos de ejemplo (¡IMPORTANTE!)
python scripts/populate_all.py

# Verificar datos (opcional)
python scripts/check_db.py
```

### 4. Ejecutar el Sistema
```bash
python manage.py runserver
```

**🎉 ¡Listo! Accede a: http://127.0.0.1:8000/**

## 👥 Usuarios de Prueba

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `c.morales@colegio.cl` | `password123` | Profesor | Carmen Morales |
| `v.lagos@colegio.cl` | `password123` | Estudiante | Valentina Lagos |
| `r.paredes@colegio.cl` | `password123` | Soporte | Ricardo Paredes |
| `admin@colegio.cl` | `password123` | Admin | Administrador |

**💡 Consejo**: Inicia con el usuario estudiante para probar el flujo básico de reservas.

## 🎯 Flujo de Prueba Recomendado

1. **Login como estudiante** → `v.lagos@colegio.cl` / `password123`
2. **Explorar salas** → Ver catálogo y filtros
3. **Hacer una reserva** → Seleccionar sala y horario
4. **Ver dashboard** → Gestionar reservas
5. **Probar sistema de valoración** → Ir a una reserva completada y calificarla

## 🏗️ Características Principales

### 👤 **Gestión de Usuarios**
- **Registro y autenticación** con roles diferenciados
- **Dashboard personalizado** por tipo de usuario
- **Perfiles con información** académica y de contacto

### 🏠 **Gestión de Salas**
- **Catálogo completo** con 10 salas de ejemplo
- **Búsqueda y filtrado** por capacidad, ubicación y equipamiento
- **Sistema de disponibilidad** en tiempo real

### 📅 **Sistema de Reservas**
- **Reservas intuitivas** con validación automática
- **Gestión de estados**: Pendiente, Confirmada, Completada, Cancelada
- **Cancelación permitida** hasta 1 hora antes

### ⭐ **Sistema de Calificaciones**
- **Reseñas detalladas** (limpieza, equipamiento, comodidad)
- **Categorización de comentarios** (positivo, sugerencia, problema)
- **Estadísticas** por sala y usuario

## 🛠️ Tecnologías

- **Backend**: Django 5.2.1 (Python)
- **Frontend**: Bootstrap 5 + FontAwesome
- **Base de Datos**: SQLite (desarrollo)
- **Autenticación**: Django Auth System

## 📁 Estructura del Proyecto

```
Final_QA/
├── README.md                    # Este archivo
└── proyecto_calidad/           # Proyecto Django principal
    ├── manage.py               # Comando Django
    ├── requirements.txt        # Dependencias
    ├── db.sqlite3             # Base de datos
    ├── scripts/               # 📁 Scripts de utilidad
    │   ├── README.md          # Documentación de scripts
    │   ├── populate_all.py    # Script principal de poblado
    │   ├── populate_users.py  # Crear usuarios
    │   ├── populate_rooms.py  # Crear salas
    │   └── tests/             # Scripts de testing
    ├── templates/             # Templates HTML
    ├── logs/                  # Archivos de log
    ├── core/                 # App principal
    ├── usuarios/             # App de usuarios
    ├── rooms/                # App de salas y reservas
    └── proyecto_calidad/     # Configuración Django
```

## 🔍 Funcionalidades por Rol

### 👨‍🎓 **Estudiantes**
- ✅ Ver y buscar salas disponibles
- ✅ Realizar reservas en salas permitidas
- ✅ Gestionar sus reservas (ver, cancelar)
- ✅ Calificar salas después del uso
- ✅ Ver historial personal

### 👨‍🏫 **Profesores**
- ✅ Todas las funcionalidades de estudiantes
- ✅ Acceso a todos los tipos de salas
- ✅ Reservas con mayor flexibilidad
- ✅ Dashboard académico

### 👨‍💼 **Administradores**
- ✅ Todas las funcionalidades anteriores
- ✅ Crear y editar salas
- ✅ Gestionar todas las reservas
- ✅ Ver estadísticas del sistema
- ✅ Panel de administración Django

## 🧪 Testing y Depuración

### Scripts de Testing Disponibles
```bash
# Test completo del sistema de valoración
python scripts/tests/test_review_system.py

# Test de todos los escenarios de usuario
python scripts/tests/test_all_user_scenarios.py

# Verificar estado de la base de datos
python scripts/check_db.py
```

### Logs del Sistema
- **Ubicación**: `logs/debug.log`
- **Contenido**: Errores, accesos, reservas, operaciones admin

### Panel de Administración Django
- **URL**: http://127.0.0.1:8000/admin/
- **Usuario**: `admin@colegio.cl` / `password123`

## 🚨 Solución de Problemas

### Error: "No module named 'django'"
```bash
# Verificar que el entorno virtual esté activado
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstalar dependencias si es necesario
pip install -r requirements.txt
```

### Error: "Database locked"
```bash
# Cerrar el servidor de desarrollo (Ctrl+C)
# Luego ejecutar los scripts
```

### Error: "Apps aren't loaded yet"
```bash
# Ejecutar scripts desde la raíz del proyecto
cd proyecto_calidad
python scripts/populate_all.py
```

### No hay datos en el sistema
```bash
# Ejecutar el script de poblado
python scripts/populate_all.py

# Verificar que se crearon los datos
python scripts/check_db.py
```

## 📊 Datos de Ejemplo Incluidos

- **👥 Usuarios**: 15+ usuarios con diferentes roles
- **🏠 Salas**: 10 salas con características variadas
- **📅 Reservas**: 30+ reservas en diferentes estados
- **⭐ Reseñas**: Sistema listo para testing de valoraciones

## 🔒 Seguridad Implementada

- ✅ **Validación de formularios** robusta
- ✅ **Autorización por roles** en todas las vistas
- ✅ **Protección CSRF** en formularios
- ✅ **Manejo de errores** centralizado
- ✅ **Logging completo** para auditoría
- ✅ **Robots.txt** para ocultar rutas administrativas

## 🚀 Para Desarrollo Avanzado

### Comandos Django Útiles
```bash
# Crear migraciones después de cambios en modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario adicional
python manage.py createsuperuser

# Recopilar archivos estáticos (producción)
python manage.py collectstatic
```

### Agregar Nuevos Datos
```bash
# Ejecutar scripts individuales
python manage.py shell < scripts/populate_users.py
python manage.py shell < scripts/populate_rooms.py
python manage.py shell < scripts/generate_reservations.py
```

## 📞 Soporte

- 📁 **Scripts**: Ver `scripts/README.md` para documentación detallada
- 📊 **Logs**: Revisar `logs/debug.log` para errores
- ⚙️ **Configuración**: Ver `proyecto_calidad/settings.py`
- 🧪 **Testing**: Ejecutar scripts en `scripts/tests/`

---

**🎓 Desarrollado para el curso de Calidad de Software**
**💻 Sistema completo con autenticación, reservas y valoraciones**

## 👥 Usuarios de Prueba

El sistema incluye dos grupos de usuarios de prueba:

### Usuarios específicos (formato n.apellido@colegio.cl)

El script `populate_users.py` crea usuarios con diferentes roles:

| Correo Electrónico | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `c.morales@colegio.cl` | `password123` | Profesor | Carmen Morales |
| `r.gomez@colegio.cl` | `password123` | Profesor | Roberto Gómez |
| `c.vega@colegio.cl` | `password123` | Profesor | Claudia Vega |
| `v.lagos@colegio.cl` | `password123` | Estudiante | Valentina Lagos |
| `m.fuentes@colegio.cl` | `password123` | Estudiante | Matías Fuentes |
| `r.paredes@colegio.cl` | `password123` | Soporte | Ricardo Paredes |

**Nota**: Todos los usuarios creados por este script usan la contraseña `password123`.

### Usuarios adicionales (si existen en el sistema)

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `estudiante1` | `EstudiantePass123` | Estudiante | Usuario estudiante básico |
| `estudiante2` | `EstudiantePass123` | Estudiante | Usuario estudiante básico |
| `profesor1` | `ProfesorPass123` | Profesor | Usuario con permisos de profesor |
| `coordinador` | `CoordinadorPass123` | Admin | Usuario administrador |
| `admin` | `Django12345!` | Superuser | Superusuario del sistema |

## 🏠 Salas de Ejemplo

El sistema incluye 10 salas de ejemplo con diferentes características:

- **Sala Silenciosa A1** - Estudio individual (12 personas)
- **Sala Colaborativa B2** - Trabajo en grupo (8 personas)
- **Sala de Computación C3** - Proyectos digitales (15 personas)
- **Sala Ejecutiva D4** - Reuniones formales (6 personas)
- **Aula Magna E5** - Eventos grandes (50 personas)
- **Cabina Individual F6** - Concentración máxima (1 persona)
- **Sala de Innovación G7** - Lluvia de ideas (10 personas)
- **Biblioteca Digital H8** - Recursos híbridos (20 personas)
- **Sala Wellness I9** - Ambiente relajante (8 personas)
- **Centro de Idiomas J10** - Práctica multiidioma (12 personas)

## 🗂️ Estructura del Proyecto

```
proyecto_calidad/
├── manage.py                    # Comando principal de Django
├── populate_all.py             # Script maestro para poblar la base de datos
├── populate_users.py           # Script para crear usuarios con diferentes roles
├── populate_rooms.py           # Script para crear salas de diferentes tipos
├── generate_reservations.py    # Script para generar reservas de prueba
├── requirements.txt            # Dependencias del proyecto
├── db.sqlite3                  # Base de datos SQLite
├── logs/                       # Archivos de logging
├── templates/                  # Templates HTML
│   ├── base.html               # Template base
│   ├── rooms/                  # Templates de salas
│   ├── usuarios/               # Templates de usuarios
│   └── errors/                 # Templates de errores
├── core/                     # App principal
├── usuarios/                 # App de gestión de usuarios
│   ├── models.py            # Modelo CustomUser
│   ├── views.py             # Vistas de autenticación
│   ├── forms.py             # Formularios de usuario
│   └── urls.py              # URLs de usuarios
├── rooms/                   # App de gestión de salas
│   ├── models.py           # Modelos Room, Reservation, Review
│   ├── views.py            # Vistas de salas y reservas
│   ├── forms.py            # Formularios de reservas
│   ├── admin.py            # Configuración admin
│   └── urls.py             # URLs de salas
└── proyecto_calidad/       # Configuración del proyecto
    ├── settings.py         # Configuración Django
    ├── urls.py            # URLs principales
    └── wsgi.py            # WSGI config
```

## 🔍 Funcionalidades por Rol

### 👨‍🎓 **Estudiantes**
- Ver catálogo de salas disponibles
- Buscar y filtrar salas
- Realizar reservas
- Gestionar sus reservas
- Calificar salas utilizadas
- Ver historial de reservas

### 👨‍🏫 **Profesores**
- Todas las funcionalidades de estudiantes
- Acceso a salas premium
- Reservas con prioridad
- Dashboard académico

### 👨‍💼 **Coordinadores/Administradores**
- Todas las funcionalidades anteriores
- Crear y editar salas
- Gestionar todas las reservas
- Ver estadísticas del sistema
- Acceso al panel de administración Django

## 🧪 Testing Manual

### Flujo Básico de Reserva:
1. **Navegar** a http://127.0.0.1:8000/
2. **Iniciar sesión** con `estudiante1` / `EstudiantePass123`
3. **Explorar salas** disponibles
4. **Seleccionar una sala** y ver detalles
5. **Hacer una reserva** especificando fecha/hora
6. **Confirmar reserva** y verificar en dashboard
7. **Calificar la sala** después del uso (cambiar estado manualmente)

## 📊 Monitoreo y Logs

El sistema incluye logging completo en `logs/debug.log`:
- Acciones de usuarios
- Errores y excepciones
- Reservas creadas/canceladas
- Accesos a salas
- Operaciones administrativas

## 🔒 Seguridad Implementada

- **Validación de entrada**: Formularios con validación robusta
- **Autorización**: Decoradores para control de acceso
- **Protección CSRF**: Tokens en todos los formularios
- **Manejo de errores**: Captura y logging de excepciones
- **Sanitización**: Escape de datos en templates

## 🚀 Despliegue en Producción

Para desplegar en producción, considera:

1. **Base de datos**: Migrar a PostgreSQL/MySQL
2. **Variables de entorno**: Usar `python-decouple`
3. **Archivos estáticos**: Configurar `whitenoise` o CDN
4. **Servidor**: Usar `gunicorn` + Nginx
5. **Monitoreo**: Implementar logging avanzado
6. **Backup**: Configurar respaldos automáticos

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Proyecto desarrollado para el curso de Calidad de Software.

## 📞 Soporte

Para dudas o problemas:
- Revisar logs en `logs/debug.log`
- Verificar configuración en `settings.py`
- Consultar documentación de Django

---

**Desarrollado con ❤️ usando Django | Proyecto de Calidad de Software**

