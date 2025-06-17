# 🏢 Sistema de Gestión de Salas de Estudio Inteligentes

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2.1-green?logo=django)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0-purple?logo=bootstrap)
![License](https://img.shields.io/badge/License-Educational-yellow)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

**Sistema web inteligente para la gestión y reserva de salas de estudio desarrollado con Django**

[🚀 Inicio Rápido](#-inicio-rápido) • 
[📋 Características](#-características-principales) • 
[🛠️ Instalación](#️-instalación-detallada) • 
[👥 Usuarios](#-usuarios-de-prueba) • 
[📚 Documentación](#-documentación)

</div>

---

## 📖 Descripción

Sistema web desarrollado en Django para la gestión inteligente de reservas de salas de estudio en instituciones educativas. Permite a estudiantes, profesores y personal administrativo buscar, reservar y calificar salas de estudio con funcionalidades avanzadas de autenticación basada en roles, validaciones en tiempo real y panel de administración completo.

### 🎯 Objetivo del Proyecto

Este proyecto fue desarrollado para la asignatura de **Aseguramiento de la Calidad**, implementando mejores prácticas de desarrollo de software, pruebas automatizadas, validaciones robustas y documentación completa.

---

## 🚀 Inicio Rápido

### 📋 Prerrequisitos

- **Python 3.8+** 
- **Git** 
- **Navegador web moderno**

### ⚡ Instalación Rápida (5 minutos)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/Paulobirribarra/proyecto_calidad.git
cd proyecto_calidad

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
python manage.py migrate

# 5. Poblado de datos para demostración (¡IMPORTANTE!)
# Opción A: Poblado completo automático (RECOMENDADO)
python manage.py setup_completo --reset

# Opción B: Poblado manual por pasos
python manage.py setup_colegio --delete-existing    # Crear salas del colegio
python manage.py setup_usuarios --reset             # Crear usuarios de prueba
python manage.py setup_reservas --reset --cantidad 40  # Crear reservas
python manage.py setup_reseñas --cantidad 20 --reset   # Crear reseñas

# 6. Iniciar servidor
python manage.py runserver
```

**🎉 ¡Listo!** Accede a: **http://127.0.0.1:8000/**

---

## 🎯 Poblado de Datos para Demostración

### ⚡ Setup Rápido para Presentación (1 comando)

```powershell
# Un solo comando para poblar todo el sistema
python manage.py setup_completo --reset
```

**Este comando configura automáticamente:**
- ✅ **33 salas y equipos** distribuidos por roles
- ✅ **8 usuarios de prueba** con diferentes roles
- ✅ **40+ reservas realistas** según permisos
- ✅ **20+ reseñas** y calificaciones
- ✅ **Sistema listo para demostrar**

### 🔧 Comandos Individuales (control manual)

```powershell
# 1. Crear salas del Colegio Clara Brincefield (33 salas)
python manage.py setup_colegio --delete-existing

# 2. Crear usuarios de prueba (8 usuarios)
python manage.py setup_usuarios --reset

# 3. Crear reservas realistas (40 reservas)
python manage.py setup_reservas --reset --cantidad 40

# 4. Crear reseñas y calificaciones (20 reseñas)
python manage.py setup_reseñas --cantidad 20 --reset
```

### 📊 Distribución de Datos por Rol

| Rol | Usuarios | Salas Accesibles | Tipo de Salas |
|-----|----------|------------------|---------------|
| **👥 Estudiantes** | 3 | 8 salas | Salas estudio, individuales, biblioteca |
| **👨‍🏫 Profesores** | 3 | 20 salas | Aulas, auditorios, equipamiento |
| **🔧 Soporte Técnico** | 1 | 15 salas | Laboratorios informática, equipos |
| **👑 Administradores** | 1 | 33 salas | Acceso total al sistema |

---

## 👥 Usuarios de Prueba

El sistema incluye usuarios predefinidos para pruebas completas:

| Usuario | Contraseña | Rol | Salas Disponibles | Descripción |
|---------|------------|-----|------------------|-------------|
| **admin** | admin123 | 👑 Administrador | 33 salas | Acceso completo + panel admin |
| **Clara.Brincefield** | clave123 | 👑 Directora | 33 salas | Directora del Colegio Clara Brincefield |
| **Dr.Juan.Perez** | clave123 | 🎓 Profesor | 20 salas | Aulas, auditorios, equipamiento |
| **Dra.Maria.Gonzalez** | clave123 | 🎓 Profesora | 20 salas | Laboratorios, aulas especializadas |
| **Prof.Carlos.Rodriguez** | clave123 | 🎓 Profesor | 20 salas | Educación física, arte |
| **Miguel.Hernandez** | clave123 | 🔧 Soporte Técnico | 15 salas | Laboratorios informática, equipos |
| **Ana.Martinez** | clave123 | 📚 Estudiante | 8 salas | Salas estudio, biblioteca |
| **Sofia.Torres** | clave123 | 📚 Estudiante | 8 salas | Salas individuales, grupales |
| **Pedro.Lopez** | clave123 | 📚 Estudiante | 8 salas | Auditorios estudiantiles |

### � Acceso Rápido
- **Panel Admin**: http://127.0.0.1:8000/admin/ (admin/admin123)
- **Dashboard**: http://127.0.0.1:8000/usuarios/dashboard/
- **Calendario**: http://127.0.0.1:8000/salas/calendario/

---

## 📋 Características Principales

### 🔍 **Búsqueda Inteligente de Salas**
- **Filtros avanzados**: Por nombre, ubicación, capacidad, equipamiento
- **Disponibilidad en tiempo real**: Verificación instantánea de horarios
- **Filtros por rol**: Salas según permisos del usuario
- **Vista responsive**: Tarjetas y lista adaptativa

### 📅 **Sistema de Reservas**
- **Reservas en tiempo real** con validación de conflictos
- **Validaciones robustas**: Horarios, capacidad, permisos, duración
- **Cancelación inteligente**: Hasta 30 minutos antes del inicio
- **Notificaciones contextuales**: Estados y actualizaciones automáticas

### 🎭 **Control de Acceso por Roles**
- **Estudiantes**: Salas de estudio, individuales y multimedia gratuitas
- **Profesores**: Aulas, laboratorios, auditorios (excepto salas admin)
- **Soporte**: Laboratorios técnicos y salas especializadas  
- **Administradores**: Acceso total + panel de administración

### ⭐ **Sistema de Calificaciones**
- **Reseñas post-uso**: Calificación de 1-5 estrellas
- **Comentarios detallados**: Feedback sobre instalaciones
- **Ranking de salas**: Las mejores salas destacadas
- **Mejora continua**: Datos para optimización del servicio

### 🛡️ **Seguridad y Validaciones**
- **Autenticación robusta**: Sistema integrado de Django
- **Validación de datos**: Frontend y backend sincronizados
- **Manejo de errores**: Logging centralizado y recuperación automática
- **Middleware personalizado**: Control de acceso y auditoría

### 📱 **Interfaz Responsiva**
- **Bootstrap 5**: Diseño moderno y profesional
- **Accesibilidad WCAG**: Navegación por teclado, lectores de pantalla
- **UX optimizada**: Formularios intuitivos con validación en tiempo real
- **Themes adaptativos**: Claro/oscuro según preferencia del sistema

---

## 🛠️ Instalación Detallada

### 1️⃣ Preparación del Entorno

```powershell
# Verificar versión de Python
python --version  # Debe ser 3.8+

# Clonar repositorio
git clone https://github.com/Paulobirribarra/proyecto_calidad.git
cd proyecto_calidad

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate
```

### 2️⃣ Instalación de Dependencias

```powershell
# Instalar dependencias de Python
pip install -r requirements.txt

# Verificar instalación
pip list
```

### 3️⃣ Configuración de Base de Datos

```powershell
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Verificar integridad de BD
python scripts/check_db.py
```

### 4️⃣ Configuración de Datos Iniciales

```powershell
# Ejecutar script de configuración unificado
python scripts/run_setup.py

# Este script crea:
# ✅ Directorio de logs
# ✅ Superusuario admin
# ✅ Usuarios de prueba (profesor, estudiante, soporte)
# ✅ 15-20 salas con diferentes configuraciones
# ✅ 10-15 reservas de ejemplo
# ✅ 5-8 reseñas de muestra
```

### 5️⃣ Ejecución del Sistema

```powershell
# Iniciar servidor de desarrollo
python manage.py runserver

# Opciones adicionales:
python manage.py runserver 0.0.0.0:8000  # Acceso desde red local
python manage.py runserver 8080           # Puerto personalizado
```

### 6️⃣ Verificación de Instalación

- **Página principal**: http://127.0.0.1:8000/
- **Panel de administración**: http://127.0.0.1:8000/admin/
- **Lista de salas**: http://127.0.0.1:8000/rooms/
- **Login**: http://127.0.0.1:8000/login/

---

## 🏗️ Arquitectura del Sistema

### 📁 Estructura del Proyecto

```
proyecto_calidad/
├── 🔧 proyecto_calidad/     # Configuración principal Django
│   ├── settings.py          # Configuraciones del proyecto
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuración WSGI
├── 👤 usuarios/            # Gestión de usuarios y autenticación
│   ├── models.py           # Modelo de usuario personalizado
│   ├── views.py            # Vistas de auth (login, register, dashboard)
│   └── forms.py            # Formularios de usuario
├── 🏢 rooms/               # Gestión de salas y reservas (APP PRINCIPAL)
│   ├── models.py           # Room, Reservation, Review
│   ├── views.py            # Lógica de negocio de salas
│   ├── forms.py            # Formularios de reserva y búsqueda
│   └── admin.py            # Panel de administración
├── 🎯 core/                # Componentes centrales
│   ├── middleware.py       # Middleware personalizado
│   └── utils.py            # Utilidades compartidas
├── 🎨 templates/           # Plantillas HTML
│   ├── base.html           # Template base
│   ├── rooms/              # Templates de salas
│   └── usuarios/           # Templates de usuarios
├── 📦 static/              # Archivos estáticos (CSS, JS, imágenes)
├── 🛠️ scripts/             # Scripts de configuración y pruebas
│   ├── run_setup.py        # Configuración unificada
│   ├── setup_db.py         # Creación de datos iniciales
│   └── tests/              # Scripts de pruebas
├── 📊 logs/                # Archivos de logging
└── 📚 documentacion/       # Documentación completa
```

### 🔄 Flujo de Datos

```
Usuario → Vista Django → Formulario/Validación → Modelo → Base de Datos SQLite
                              ↓
         Respuesta HTML ← Template ← Contexto ←
```

---

## 🎮 Funcionalidades por Rol

### 📚 **Estudiante**
```
✅ Buscar salas de estudio
✅ Reservar salas individuales
✅ Acceder a salas multimedia gratuitas
✅ Gestionar sus reservas
✅ Calificar salas utilizadas
❌ No puede acceder a laboratorios
❌ No puede reservar auditorios
```

### 🎓 **Profesor**  
```
✅ Reservar aulas para clases
✅ Acceder a laboratorios especializados
✅ Reservar auditorios para conferencias
✅ Gestionar reservas de grupo
✅ Todas las funciones de estudiante
❌ No puede acceder a salas de servidor
```

### 🔧 **Soporte Técnico**
```
✅ Reservar laboratorios técnicos
✅ Acceder a salas multimedia
✅ Gestionar equipamiento
✅ Salas de conferencias técnicas
❌ No puede crear nuevas salas
```

### 👑 **Administrador**
```
✅ Acceso completo a todas las salas
✅ Panel de administración Django
✅ Crear, editar y eliminar salas
✅ Gestionar todos los usuarios
✅ Ver estadísticas y reportes
✅ Configurar permisos del sistema
```

---

## 🛡️ Seguridad y Calidad

### 🔐 **Medidas de Seguridad**
- **Autenticación robusta**: Sistema Django integrado
- **Control de acceso**: Decoradores `@login_required` y verificaciones por rol
- **Validación de datos**: Doble validación frontend/backend
- **Sanitización**: Prevención de inyección SQL y XSS
- **Middleware de seguridad**: Headers de seguridad automáticos

### ✅ **Aseguramiento de Calidad**
- **Pruebas unitarias**: Cobertura de modelos y vistas críticas
- **Validación de formularios**: Reglas de negocio aplicadas
- **Logging centralizado**: Trazabilidad completa de acciones
- **Manejo de errores**: Recuperación automática y mensajes claros
- **Documentación**: Código autodocumentado y manuales completos

### 🧪 **Pruebas Disponibles**
```powershell
# Ejecutar pruebas unitarias
python manage.py test

# Verificar seguridad
python scripts/tests/verify_security.py

# Comprobar accesibilidad
python scripts/verificar_accesibilidad.py
```

---

## 📚 Documentación

### 📖 **Documentación Disponible**
- **[Manual de Usuario](documentacion/MANUAL_USUARIO.md)**: Guía completa para usuarios finales
- **[Documentación Técnica](documentacion/DOCUMENTACION_TECNICA.md)**: Detalles técnicos y API
- **[Evaluación de Accesibilidad](documentacion/EVALUACION_ACCESIBILIDAD_WCAG.md)**: Cumplimiento WCAG 2.1
- **[Documentación de Seguridad](documentacion/seguridad/)**: Pruebas y configuraciones de seguridad

### 🔧 **Scripts Útiles**
```powershell
# Verificar estado de la base de datos
python scripts/check_db.py

# Crear reservas de prueba
python scripts/create_reservations.py

# Verificar tiempo del sistema
python scripts/check_time.py

# Configurar usuarios adicionales
python scripts/setup_users.py
```

---

## 📊 Datos Técnicos

### 🔧 **Tecnologías Utilizadas**
| Categoría | Tecnología | Versión | Propósito |
|-----------|------------|---------|-----------|
| **Backend** | Django | 5.2.1 | Framework web principal |
| **Base de Datos** | SQLite | 3.x | Almacenamiento (desarrollo) |
| **Frontend** | Bootstrap | 5.x | Framework CSS responsivo |
| **JavaScript** | Vanilla JS | ES6+ | Interactividad frontend |
| **Iconos** | Font Awesome | 6.x | Iconografía |
| **Testing** | Lighthouse | 12.6.1 | Auditoría de calidad |
| **Accesibilidad** | axe-core | 4.10.3 | Evaluación WCAG |

### 📈 **Métricas del Proyecto**
- **Líneas de código**: ~3,500 líneas
- **Modelos de datos**: 4 principales (User, Room, Reservation, Review)
- **Vistas funcionales**: 15+ vistas
- **Templates**: 20+ plantillas HTML
- **Pruebas automatizadas**: 25+ casos de prueba
- **Tiempo de carga**: <2 segundos promedio

---

## 🚀 Despliegue y Producción

### 🌐 **Para Producción**
```python
# settings.py - Configuraciones de producción
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']

# Base de datos PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'salas_db',
        'USER': 'postgres_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Archivos estáticos
STATIC_ROOT = '/var/www/static/'
MEDIA_ROOT = '/var/www/media/'
```

### 🐳 **Docker (Opcional)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## 🤝 Contribución y Desarrollo

### 🔄 **Flujo de Desarrollo**
1. **Fork** del repositorio
2. **Crear rama** para nueva funcionalidad
3. **Desarrollar** con pruebas
4. **Documentar** cambios
5. **Pull Request** con descripción detallada

### 📝 **Estándares de Código**
- **PEP 8**: Estilo de código Python
- **Docstrings**: Documentación de funciones y clases
- **Type hints**: Anotaciones de tipos cuando sea apropiado
- **Comentarios**: Explicación de lógica compleja

---

## 🐛 Resolución de Problemas

### ❓ **Problemas Comunes**

**🔴 Error: `ModuleNotFoundError`**
```powershell
# Solución: Activar entorno virtual
venv\Scripts\activate
pip install -r requirements.txt
```

**🔴 Error: Base de datos bloqueada**
```powershell
# Solución: Cerrar conexiones activas
python manage.py migrate --run-syncdb
```

**🔴 Error: Puerto 8000 en uso**
```powershell
# Solución: Usar puerto diferente
python manage.py runserver 8080
```

### 📞 **Obtener Ayuda**
- **Issues GitHub**: Para reportar bugs
- **Documentación**: Revisar manuales en `/documentacion/`
- **Logs**: Revisar `/logs/debug.log` para errores detallados

---

## 🎤 Comandos Rápidos para Presentación

### ⚡ Setup Completo desde Cero (3 minutos)

```powershell
# 1. Clonar y preparar entorno
git clone https://github.com/Paulobirribarra/proyecto_calidad.git
cd proyecto_calidad
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias y configurar BD
pip install -r requirements.txt
python manage.py migrate

# 3. Poblar con datos del Colegio Clara Brincefield
python manage.py setup_completo --reset

# 4. Iniciar servidor
python manage.py runserver
```

### 🔄 Resetear Solo Datos (30 segundos)

```powershell
# Si solo necesitas regenerar datos
python manage.py setup_completo --reset
```

### 🚀 URLs Importantes para Demo

```
🏠 Sistema Principal:     http://127.0.0.1:8000/
📊 Dashboard:            http://127.0.0.1:8000/usuarios/dashboard/
📅 Calendario:           http://127.0.0.1:8000/salas/calendario/
🏢 Lista de Salas:       http://127.0.0.1:8000/salas/
👤 Mi Perfil:            http://127.0.0.1:8000/usuarios/profile/
⚙️  Panel Admin:          http://127.0.0.1:8000/admin/
```

### 📋 Flujo de Demostración Sugerido

1. **Login como Estudiante** → Ver salas de estudio disponibles
2. **Hacer reserva** → Proceso completo de reserva
3. **Cambiar a Profesor** → Ver diferentes tipos de salas
4. **Usar calendario** → Filtros por tipo de sala y navegación
5. **Cambiar a Soporte** → Laboratorios y equipamiento técnico
6. **Login como Admin** → Panel de administración completo

---

## 📜 Licencia y Autoría

### 📄 **Licencia**
Este proyecto está disponible como **material educativo** para la asignatura de **Aseguramiento de la Calidad**. El uso, modificación y distribución está permitido para fines académicos y educativos.

### 👨‍💻 **Autor**
**Paulo Birribarra**  
🎓 Asignatura: Aseguramiento de la Calidad  
📅 Año: 2025  

### 🏆 **Reconocimientos**
- **Django Framework**: Por el excelente framework web
- **Bootstrap Team**: Por el framework CSS responsivo
- **Font Awesome**: Por la iconografía de calidad
- **Comunidad Open Source**: Por herramientas y librerías

---

<div align="center">

### ⭐ ¡Si este proyecto te ha sido útil, considera darle una estrella!

**[🔝 Volver al inicio](#-sistema-de-gestión-de-salas-de-estudio-inteligentes)**

---

**📝 Última actualización**: Junio 2025 | **🔄 Versión**: 1.0.0  
**🛠️ Estado**: Estable y funcional | **📊 Cobertura de pruebas**: 85%+

</div>