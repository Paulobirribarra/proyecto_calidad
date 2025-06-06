"""
Script para ejecutar setup_db.py de manera adecuada.

Este script es un wrapper que ejecuta setup_db.py en el entorno correcto de Django.
"""

import os
import sys
import importlib.util

# Asegurar que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
import django
django.setup()

# Cargar el script setup_db.py usando importlib
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup_db.py')

spec = importlib.util.spec_from_file_location("setup_db", script_path)
setup_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup_db)

# Ejecutar la función principal
if __name__ == "__main__":
    try:
        setup_db.configurar_base_datos()
    except Exception as e:
        print(f"\n¡ERROR! No se pudo configurar la base de datos: {e}")
        sys.exit(1)
