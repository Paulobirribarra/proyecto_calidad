# Sistema de Gestión de Salas de Estudio - Scripts de Datos

Este directorio contiene varios scripts para poblar la base de datos con datos de prueba.

## Scripts disponibles

- `populate_all.py`: Script maestro que ejecuta todos los demás scripts en secuencia
- `populate_users.py`: Crea usuarios con diferentes roles (profesor, estudiante, soporte)
- `populate_rooms.py`: Crea salas de diferentes tipos con permisos específicos
- `generate_reservations.py`: Genera reservas aleatorias para probar el sistema

## Cómo ejecutar los scripts

### 1. Ejecutar todos los scripts

```bash
python populate_all.py
```

### 2. Ejecutar scripts individuales

```bash
# Para usuarios
python manage.py shell < populate_users.py

# Para salas
python manage.py shell < populate_rooms.py

# Para reservas
python manage.py shell < generate_reservations.py
```

## Contraseñas de usuarios

Todos los usuarios creados con estos scripts tienen la contraseña: `password123`

- Formato de correo electrónico: `inicial.apellido@colegio.cl` (ej. `c.morales@colegio.cl`)
- Roles: profesor, estudiante, soporte

Para más detalles, consulta el README principal en el directorio raíz.
