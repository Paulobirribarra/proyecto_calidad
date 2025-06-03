# 📚 Scripts del Sistema de Gestión de Salas

Este directorio contiene scripts para configurar, probar y mantener el Sistema de Gestión de Salas.

## 🔧 Scripts Principales

### `run_setup.py`
Script principal para configurar el sistema desde cero. Ejecuta automáticamente `setup_db.py`.

**Uso:**
```powershell
python scripts\run_setup.py
```

**Acciones que realiza:**
- Crea el directorio de logs si no existe
- Crea superusuario y usuarios predefinidos
- Crea salas de diferentes tipos
- Genera reservas aleatorias de prueba
- Genera reseñas para algunas reservas

### `setup_db.py`
Script interno que contiene la lógica de configuración. Es llamado por `run_setup.py`.

**Funciones principales:**
- `crear_directorio_logs()` - Crea la carpeta de logs
- `crear_superusuario()` - Configura el usuario administrador
- `crear_usuarios(cantidad)` - Genera usuarios variados
- `crear_salas(cantidad)` - Configura las salas disponibles
- `generar_reservas(cantidad_por_usuario)` - Crea reservas aleatorias

### `check_db.py`
Script para verificar la integridad de la base de datos.

**Uso:**
```powershell
python scripts\check_db.py
```

## 📁 Directorio `tests`

Este subdirectorio contiene scripts para probar diferentes aspectos del sistema:

- `test_security_vulnerabilities.py` - Pruebas de seguridad básicas
- `test_reservation_simulation.py` - Simulación del flujo de reservas
- `test_review_system.py` - Pruebas del sistema de reseñas
- `test_all_user_scenarios.py` - Pruebas de diferentes escenarios de usuario

## 🚀 Configuración Rápida

Para configurar rápidamente el sistema completo:

1. Eliminar base de datos previa (si existe)
   ```powershell
   if (Test-Path db.sqlite3) { Remove-Item db.sqlite3 }
   ```

2. Aplicar migraciones
   ```powershell
   python manage.py migrate
   ```

3. Ejecutar script de configuración
   ```powershell
   python scripts\run_setup.py
   ```

## 📝 Notas

- Los scripts deben ejecutarse desde la raíz del proyecto Django (`proyecto_calidad/`)
- Se recomienda activar el entorno virtual antes de ejecutar los scripts
- Si ocurren errores, revisar los logs en `logs/debug.log`