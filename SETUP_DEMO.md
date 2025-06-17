# 🎯 Setup Rápido para Demostración - Colegio Clara Brincefield

## ⚡ Setup Completo (3 minutos)

```powershell
# 1. Clonar repositorio
git clone https://github.com/Paulobirribarra/proyecto_calidad.git
cd proyecto_calidad

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
python manage.py migrate

# 5. Poblar datos del Colegio Clara Brincefield
python manage.py setup_completo --reset

# 6. Iniciar servidor
python manage.py runserver
```

## 🚀 Acceso al Sistema

**URL Principal**: http://127.0.0.1:8000/

## 👥 Usuarios para Demo

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| **admin** | admin123 | 👑 Admin | Panel administración completo |
| **Clara.Brincefield** | clave123 | 👑 Directora | Directora del colegio |
| **Dr.Juan.Perez** | clave123 | 🎓 Profesor | Profesor de matemáticas |
| **Miguel.Hernandez** | clave123 | 🔧 Soporte | Técnico de sistemas |
| **Ana.Martinez** | clave123 | 📚 Estudiante | Estudiante de secundaria |

## 📊 Datos Generados

- ✅ **33 salas y equipos** del Colegio Clara Brincefield
- ✅ **8 usuarios** con roles específicos
- ✅ **40+ reservas** realistas distribuidas en 30 días (15 completadas)
- ✅ **16+ reseñas** y calificaciones (promedio 4.0/5 estrellas)

## 🎯 Flujo de Demostración

1. **Login como Estudiante** (Ana.Martinez)
   - Ver solo salas de estudio disponibles
   - Hacer una reserva de sala individual

2. **Cambiar a Profesor** (Dr.Juan.Perez)
   - Ver aulas y laboratorios
   - Reservar un aula para clase

3. **Usar Calendario** (cualquier usuario)
   - Filtrar por tipo de sala
   - Ver reservas existentes
   - Acceder a detalles de sala desde calendario

4. **Login como Soporte** (Miguel.Hernandez)
   - Ver laboratorios de informática
   - Equipamiento técnico disponible

5. **Login como Admin** (admin)
   - Panel de administración
   - Gestión completa del sistema

## 🔄 Comandos de Mantenimiento

```powershell
# Solo resetear datos (mantener BD)
python manage.py setup_completo --reset

# Regenerar solo reservas
python manage.py setup_reservas --reset --cantidad 40

# Regenerar solo usuarios
python manage.py setup_usuarios --reset

# Ver estadísticas de poblado
python manage.py setup_colegio --delete-existing
```

## 📅 URLs Importantes

```
🏠 Inicio:               http://127.0.0.1:8000/
📊 Dashboard:            http://127.0.0.1:8000/usuarios/dashboard/
📅 Calendario:           http://127.0.0.1:8000/salas/calendario/
🏢 Lista Salas:          http://127.0.0.1:8000/salas/
👤 Perfil:               http://127.0.0.1:8000/usuarios/profile/
⚙️  Admin:                http://127.0.0.1:8000/admin/
```

## 🚨 Solución de Problemas

**Error de dependencias:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Error de base de datos:**
```powershell
python manage.py migrate --run-syncdb
```

**Puerto ocupado:**
```powershell
python manage.py runserver 8080
```

---
**📝 Nota**: Este setup genera un entorno completo para demostrar el Sistema de Gestión de Salas del Colegio Clara Brincefield con datos realistas y usuarios funcionales.
