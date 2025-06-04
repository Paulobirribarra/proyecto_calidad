# 🏢 Sistema de Gestión de Salas de Estudio Inteligentes

## 📋 Documentación Actualizada
**La documentación completa y actualizada se encuentra en el archivo README.md dentro de la carpeta `proyecto_calidad`**

Este repositorio contiene el proyecto de Sistema de Gestión de Salas de Estudio Inteligentes para la asignatura de Aseguramiento de la Calidad.

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```powershell
git clone https://github.com/Paulobirribarra/proyecto_calidad.git
cd Final_QA
```

### 2. Crear un entorno virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Configurar el proyecto
```powershell
cd proyecto_calidad
pip install -r requirements.txt
python manage.py migrate
python scripts\run_setup.py
```

### 4. Iniciar el servidor
```powershell
python manage.py runserver
```

### 5. Acceder al sistema
Abre tu navegador en: http://127.0.0.1:8000/

## 👤 Usuarios de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Administrador |
| profesor1 | profesor2023 | Profesor |
| estudiante1 | estudiante2023 | Estudiante |
| soporte1 | soporte2023 | Soporte |

## 📁 Estructura del Proyecto

- La carpeta `proyecto_calidad` contiene el proyecto Django completo
- Se ha implementado un script unificado para la configuración (`run_setup.py`)
- Todos los scripts de prueba están en la carpeta `scripts/tests/`

## 📝 Notas Importantes

Este proyecto se ha reorganizado para mejorar su estructura:
- El script de configuración unificado simplifica la instalación
- Se eliminaron scripts redundantes
- Se mejoró la documentación para facilitar la replicación del proyecto

Para ver todas las instrucciones detalladas, consulta el archivo README.md dentro de la carpeta `proyecto_calidad`.
