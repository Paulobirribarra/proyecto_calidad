# 🏢 Sistema de Gestión de Salas de Estudio Inteligentes

Sistema web desarrollado en Django para la gestión inteligente de reservas de salas de estudio. Permite a los usuarios buscar, reservar y calificar salas de estudio con funcionalidades avanzadas de autenticación, roles y administración.

## 🚀 Inicio Rápido

### 1. Prerrequisitos
- Python 3.8+
- Git

### 2. Configuración Inicial
```bash
# Clonar el repositorio
git clone https://github.com/Paulobirribarra/proyecto_calidad.git
cd proyecto_calidad

# Crear y activar entorno virtual
python -m venv venv

# Activar entorno virtual en Windows:
venv\Scripts\activate
# O en Linux/Mac:
# source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Preparación de la Base de Datos
```bash
# Eliminar base de datos anterior si existe (opcional)
# En Windows:
if exist db.sqlite3 del db.sqlite3
# En Linux/Mac:
# rm -f db.sqlite3

# Aplicar migraciones de base de datos
python manage.py migrate
```

### 4. Configuración Automática del Sistema
```bash
# Ejecutar el script de configuración unificado
# Este script realizará las siguientes tareas:
# 1. Crear el directorio de logs si no existe
# 2. Crear superusuario y usuarios de prueba
# 3. Crear salas con diferentes configuraciones
# 4. Generar reservas y reseñas de muestra
python scripts/run_setup.py
```

### 5. Ejecutar el Sistema
```bash
python manage.py runserver
```

**🎉 ¡Listo! Accede a: http://127.0.0.1:8000/**

## 👥 Usuarios de Prueba

El script de configuración crea los siguientes usuarios predefinidos:

### Administrador
- **Usuario:** admin
- **Contraseña:** admin123
- **Rol:** Administrador del sistema
- **Acceso:** Panel de administración y todas las funcionalidades

### Profesor
- **Usuario:** profesor1
- **Contraseña:** profesor2023
- **Rol:** Profesor
- **Acceso:** Reservar salas de tipo Aula, Laboratorio, Sala de conferencias y más

### Estudiante
- **Usuario:** estudiante1
- **Contraseña:** estudiante2023  
- **Rol:** Estudiante
- **Acceso:** Reservar salas de estudio y salas multimedia

### Soporte Técnico
- **Usuario:** soporte1
- **Contraseña:** soporte2023
- **Rol:** Soporte
- **Acceso:** Laboratorios, salas multimedia y de conferencias

## 🔑 Roles y Permisos

El sistema implementa un control de acceso basado en roles:

| Recurso/Acción | Estudiante | Profesor | Soporte | Admin |
|----------------|------------|----------|---------|-------|
| Salas de estudio | ✅ | ✅ | ❌ | ✅ |
| Aulas | ❌ | ✅ | ❌ | ✅ |
| Laboratorios | ❌ | ✅ | ✅ | ✅ |
| Salas conferencias | ❌ | ✅ | ✅ | ✅ |
| Salas multimedia | ✅ | ✅ | ✅ | ✅ |
| Administración | ❌ | ❌ | ❌ | ✅ |

## 📋 Características Principales

- **Búsqueda de Salas:** Filtrar por ubicación, capacidad, equipamiento y disponibilidad.
- **Gestión de Reservas:** Crear, cancelar y modificar reservas con verificación de disponibilidad.
- **Sistema de Roles:** Diferentes permisos según el tipo de usuario.
- **Notificaciones:** Alertas por email para confirmación y recordatorio de reservas.
- **Sistema de Reseñas:** Calificaciones y comentarios sobre las salas utilizadas.
- **Panel de Administración:** Gestión completa del sistema para administradores.

## ⚙️ Estructura del Proyecto

- **`proyecto_calidad/`**: Configuración principal del proyecto Django
- **`usuarios/`**: App de gestión de usuarios, autenticación y perfiles
- **`rooms/`**: App principal de gestión de salas y reservas
- **`core/`**: Componentes centrales y middleware del proyecto
- **`templates/`**: Plantillas HTML para las diferentes vistas
- **`scripts/`**: Scripts útiles para configuración y pruebas
  - **`setup_db.py`**: Script principal de configuración de la base de datos
  - **`run_setup.py`**: Script auxiliar para ejecutar la configuración
  - **`check_db.py`**: Verifica integridad de la base de datos
  - **`tests/`**: Scripts de pruebas y verificación de seguridad

## 🛠️ Desarrollo y Pruebas

### Ejecutar Pruebas Unitarias
```bash
python manage.py test
```

### Verificar Seguridad
```bash
python scripts/tests/verify_security.py
```

## 🔄 Diagrama de Flujo del Sistema

1. **Registro/Login:** Los usuarios se registran o inician sesión
2. **Búsqueda:** Los usuarios buscan salas disponibles según criterios
3. **Reserva:** Se verifica disponibilidad y permisos antes de confirmar
4. **Uso:** El usuario utiliza la sala en el horario reservado
5. **Calificación:** Después del uso, el usuario puede dejar una reseña

## 📝 Notas Importantes

1. **Script de configuración unificado**: El script `run_setup.py` ahora realiza todas las tareas de configuración en un solo paso, incluyendo la creación del directorio de logs, usuarios, salas y reservas de prueba.

2. **Base de datos**: El proyecto utiliza SQLite por defecto, lo que facilita la configuración inicial sin necesidad de servidores de bases de datos adicionales.

3. **Entorno virtual**: Se recomienda siempre usar un entorno virtual para evitar conflictos con paquetes de Python.

4. **Credenciales**: Las credenciales proporcionadas son solo para desarrollo y pruebas. En un entorno de producción, deberían utilizarse contraseñas seguras.

5. **Limpieza de scripts**: Se han eliminado los scripts redundantes y ahora solo se mantiene el script de configuración unificado para simplificar el proceso.

## 👨‍💻 Aseguramiento de la Calidad

Este proyecto ha sido desarrollado siguiendo prácticas de aseguramiento de la calidad en software, incluyendo:

- Pruebas unitarias y de integración
- Validación de datos de entrada
- Manejo adecuado de errores y excepciones
- Documentación de código
- Seguimiento de estándares de codificación Python (PEP 8)
- Control de acceso basado en roles

## 📜 Licencia

Este proyecto está disponible como material educativo para la asignatura de Aseguramiento de la Calidad.
