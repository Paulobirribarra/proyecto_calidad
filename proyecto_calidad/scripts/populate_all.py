"""
Script maestro para poblar la base de datos completa.

Este script ejecuta en secuencia los scripts:
1. populate_users.py - Crea usuarios de diferentes roles
2. populate_rooms.py - Crea salas de diferentes tipos
3. generate_reservations.py - Crea reservas para los usuarios y salas

Uso: python scripts/populate_all.py (desde la raíz del proyecto)
"""

import os
import sys
import subprocess
import django

# Cambiar al directorio padre (raíz del proyecto)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
os.chdir(project_root)

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

def ejecutar_script(script_name):
    """Ejecuta un script de Python en el entorno Django"""
    script_path = os.path.join('scripts', script_name)
    print(f"\n{'=' * 60}")
    print(f"Ejecutando {script_path}...")
    print(f"{'=' * 60}\n")
    
    try:
        # Ejecutar el script usando subprocess para capturar salida en tiempo real
        with open(script_path) as script_file:
            script_content = script_file.read()
            
        # Obtener el directorio actual para el entorno de ejecución
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Ejecutar el script usando python manage.py shell
        process = subprocess.Popen(
            [sys.executable, 'manage.py', 'shell'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=current_dir
        )
        
        # Enviar el contenido del script al proceso
        stdout, stderr = process.communicate(input=script_content)
        
        # Imprimir la salida
        print(stdout)
        
        if stderr:
            print("Errores:")
            print(stderr)
        
        print(f"\n{'=' * 60}")
        print(f"Finalizado {script_name}")
        print(f"{'=' * 60}\n")
        return process.returncode == 0
    except Exception as e:
        print(f"Error al ejecutar {script_name}: {e}")
        return False

def main():
    """Función principal que ejecuta todos los scripts de poblado"""
    print("\n" + "=" * 80)
    print("SISTEMA DE POBLADO DE BASE DE DATOS")
    print("=" * 80 + "\n")
    
    print("Este script poblará la base de datos con:")
    print("  • Usuarios con diferentes roles (profesor, estudiante, soporte)")
    print("  • Salas de diferentes tipos (aulas, salas de estudio, etc.)")
    print("  • Reservas aleatorias respetando permisos por rol\n")
    
    # Confirmar ejecución
    respuesta = input("¿Desea continuar con el poblado de datos? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada.")
        return
    
    # Ejecutar scripts en secuencia
    scripts = [
        'populate_users.py',
        'populate_rooms.py',
        'generate_reservations.py'
    ]
    
    exito = True
    for script in scripts:
        if not ejecutar_script(script):
            exito = False
            print(f"Error al ejecutar {script}. Se detendrá el proceso.")
            break
    
    if exito:
        print("\n" + "=" * 80)
        print("¡POBLADO DE BASE DE DATOS COMPLETADO CON ÉXITO!")
        print("=" * 80 + "\n")
    else:
        print("\n" + "=" * 80)
        print("EL POBLADO DE BASE DE DATOS FINALIZÓ CON ERRORES")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
