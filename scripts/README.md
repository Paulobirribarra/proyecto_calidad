# Scripts de Gestión - Colegio Clara Brincefield

Este directorio contiene los comandos de gestión de Django para configurar y poblar el sistema del Colegio Clara Brincefield con datos de ejemplo.

## Comandos Disponibles

### 🚀 Setup Completo (Recomendado)
```bash
python manage.py setup_completo --reset
```
**Ejecuta todo el proceso de configuración en orden:**
1. Configura las salas del colegio
2. Crea usuarios con diferentes roles
3. Genera reservas de ejemplo
4. Crea reseñas realistas

**Opciones:**
- `--reset`: Elimina todos los datos existentes antes de crear nuevos
- `--skip-usuarios`: Omite la creación de usuarios
- `--skip-salas`: Omite la creación de salas
- `--skip-reservas`: Omite la creación de reservas
- `--skip-reseñas`: Omite la creación de reseñas

### 📚 Configurar Salas
```bash
python manage.py setup_colegio --confirm
```
Elimina todas las salas existentes y crea las salas específicas del Colegio Clara Brincefield (aulas, laboratorios, biblioteca, etc.).

### 👥 Configurar Usuarios
```bash
python manage.py setup_usuarios --reset
```
Crea usuarios de demostración con los roles del sistema:
- **admin** / demo123 (Administrador del sistema)
- **profesor1, profesor2, profesor3** / demo123 (Profesores)
- **estudiante1, estudiante2, estudiante3** / demo123 (Estudiantes)
- **tecnico1, administrativo1, soporte1** / demo123 (Personal)

### 📅 Crear Reservas
```bash
python manage.py setup_reservas --cantidad 25 --reset
```
Genera reservas de ejemplo distribuidas en los próximos 30 días.

**Opciones:**
- `--cantidad N`: Número de reservas a crear (default: 20)
- `--reset`: Elimina reservas existentes

### ⭐ Crear Reseñas
```bash
python manage.py setup_reseñas --cantidad 20 --reset
```
Crea reseñas realistas para las salas con ratings distribuidos de forma natural.

**Opciones:**
- `--cantidad N`: Número de reseñas a crear (default: 15)
- `--reset`: Elimina reseñas existentes

## Uso Típico

### Primera configuración (proyecto nuevo):
```bash
python manage.py migrate
python manage.py setup_completo --reset
```

### Resetear solo datos de ejemplo:
```bash
python manage.py setup_completo --reset --skip-salas
```

### Agregar más datos sin eliminar existentes:
```bash
python manage.py setup_reservas --cantidad 10
python manage.py setup_reseñas --cantidad 5
```

## Credenciales de Acceso

Todos los usuarios tienen la contraseña: **demo123**

| Rol | Usuario | Email |
|-----|---------|-------|
| Administrador | admin | admin@clarabrincefield.edu |
| Profesor | profesor1 | profesor1@clarabrincefield.edu |
| Profesor | profesor2 | profesor2@clarabrincefield.edu |
| Profesor | profesor3 | profesor3@clarabrincefield.edu |
| Estudiante | estudiante1 | estudiante1@estudiantes.clarabrincefield.edu |
| Estudiante | estudiante2 | estudiante2@estudiantes.clarabrincefield.edu |
| Estudiante | estudiante3 | estudiante3@estudiantes.clarabrincefield.edu |
| Técnico | tecnico1 | tecnico1@clarabrincefield.edu |
| Administrativo | administrativo1 | admin1@clarabrincefield.edu |
| Soporte | soporte1 | soporte1@clarabrincefield.edu |

## Estructura de Archivos

```
scripts/
├── management/
│   └── commands/
│       ├── setup_completo.py      # 🚀 Comando principal
│       ├── setup_colegio.py       # 📚 Configurar salas
│       ├── setup_usuarios.py      # 👥 Crear usuarios
│       ├── setup_reservas.py      # 📅 Crear reservas
│       └── setup_reseñas.py       # ⭐ Crear reseñas
└── README.md                      # 📖 Esta documentación
```
