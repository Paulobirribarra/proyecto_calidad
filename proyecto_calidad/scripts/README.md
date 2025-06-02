# 📁 Scripts de Utilidad

Esta carpeta contiene todos los scripts de utilidad para poblar la base de datos, generar datos de prueba y ejecutar tests del sistema.

## 🚀 Scripts de Poblado de Datos

### `populate_all.py` - Script Principal
```bash
python scripts/populate_all.py
```
**Descripción**: Ejecuta automáticamente todos los scripts de poblado en el orden correcto.
- Crea usuarios con diferentes roles
- Crea salas de ejemplo
- Genera reservas de prueba

### Scripts Individuales

#### `populate_users.py` - Crear Usuarios
```bash
python manage.py shell < scripts/populate_users.py
```
**Crea usuarios con diferentes roles:**
- Profesores: `c.morales@colegio.cl`, `r.gomez@colegio.cl`, `c.vega@colegio.cl`
- Estudiantes: `v.lagos@colegio.cl`, `m.fuentes@colegio.cl`, `a.valenzuela@colegio.cl`
- Soporte: `r.paredes@colegio.cl`, `l.torres@colegio.cl`
- Administradores: `admin@colegio.cl`

**Contraseña para todos**: `password123`

#### `populate_rooms.py` - Crear Salas
```bash
python manage.py shell < scripts/populate_rooms.py
```
**Crea 10 salas de ejemplo:**
- Salas de estudio individuales y grupales
- Aulas para clases
- Laboratorios especializados
- Salas de reuniones

#### `generate_reservations.py` - Generar Reservas
```bash
python manage.py shell < scripts/generate_reservations.py
```
**Genera reservas de prueba:**
- Reservas para diferentes usuarios y roles
- Estados variados (pendiente, confirmada, completada)
- Fechas en el futuro y pasado para testing

#### `create_completed_reservations.py` - Reservas Completadas
```bash
python manage.py shell < scripts/create_completed_reservations.py
```
**Crear reservas completadas específicamente para probar el sistema de valoración**

## 🧪 Scripts de Testing

La subcarpeta `tests/` contiene varios scripts de testing:

### `test_review_system.py` - Test del Sistema de Valoración
```bash
python scripts/tests/test_review_system.py
```
**Prueba completa del sistema de valoración:**
- Validación de formularios
- Creación de reseñas
- Integración con reservas completadas

### `test_all_user_scenarios.py` - Test de Escenarios de Usuario
```bash
python scripts/tests/test_all_user_scenarios.py
```
**Prueba todos los escenarios de usuario por rol**

### `test_reservation_simulation.py` - Simulación de Reservas
```bash
python scripts/tests/test_reservation_simulation.py
```
**Simula flujos completos de reserva**

## 🔧 Scripts de Utilidad

### `check_db.py` - Verificar Base de Datos
```bash
python scripts/check_db.py
```
**Verifica el estado de la base de datos:**
- Número de usuarios, salas, reservas
- Estadísticas por rol y estado
- Integridad de datos

### `create_users.py` - Crear Usuarios Adicionales
```bash
python scripts/create_users.py
```
**Crear usuarios adicionales para testing específico**

## 🎯 Flujo Recomendado para Configuración Inicial

1. **Aplicar migraciones** (desde la raíz del proyecto):
   ```bash
   python manage.py migrate
   ```

2. **Poblar datos de ejemplo**:
   ```bash
   python scripts/populate_all.py
   ```

3. **Verificar datos**:
   ```bash
   python scripts/check_db.py
   ```

4. **Ejecutar tests** (opcional):
   ```bash
   python scripts/tests/test_review_system.py
   ```

5. **Iniciar servidor**:
   ```bash
   python manage.py runserver
   ```

## 📝 Notas Importantes

- **Orden de ejecución**: Los scripts deben ejecutarse en orden (usuarios → salas → reservas)
- **Datos de prueba**: Todos los scripts están diseñados para ser seguros de ejecutar múltiples veces
- **Logs**: Todos los scripts generan logs informativos durante la ejecución
- **Validación**: Los scripts incluyen validaciones para evitar datos duplicados

## 🚨 Troubleshooting

**Error: "No module named 'django'"**
```bash
# Activar entorno virtual primero
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

**Error: "Apps aren't loaded yet"**
```bash
# Los scripts deben ejecutarse desde la raíz del proyecto
cd proyecto_calidad
python scripts/populate_all.py
```

**Error: "Database locked"**
```bash
# Cerrar el servidor de desarrollo antes de ejecutar scripts
# Ctrl+C en la terminal del servidor
```
