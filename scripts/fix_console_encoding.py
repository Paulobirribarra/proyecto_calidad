"""
Módulo para resolver problemas de codificación con caracteres Unicode en la consola.

Este módulo configura la codificación correcta para permitir la impresión
de caracteres Unicode en consolas Windows.
"""

import sys
import os
import codecs
import platform

def fix_console_encoding():
    """
    Configura la codificación correcta para la consola.
    
    Esta función detecta el sistema operativo y configura la codificación
    adecuada para permitir caracteres Unicode en la salida estándar.
    """
    # Verificar el sistema operativo
    if platform.system() == 'Windows':
        # En Windows, configurar UTF-8 para la consola
        try:
            # Intentar configurar codificación UTF-8 para salida
            if sys.stdout.encoding != 'utf-8':
                sys.stdout.reconfigure(encoding='utf-8')
                print("Codificación de consola configurada a UTF-8")
            # Para versiones antiguas de Python que no tienen reconfigure
        except AttributeError:
            try:
                # Alternativa para versiones anteriores de Python
                import locale
                locale.setlocale(locale.LC_ALL, 'es-ES.UTF-8')
                # Redirigir stdout a un stream con la codificación correcta
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
                print("Codificación de consola configurada con codecs.getwriter")
            except (AttributeError, locale.Error):
                # Si falla, intentar otro enfoque
                os.system('chcp 65001 > nul')  # Cambiar a UTF-8 en cmd.exe
                print("Codificación de consola configurada con chcp 65001")
    else:
        # En sistemas Unix/Linux/Mac la codificación UTF-8 suele ser predeterminada
        print(f"Sistema operativo: {platform.system()}, codificación de consola: {sys.stdout.encoding}")
    
    # Verificar y mostrar la codificación actual
    print(f"Codificación de stdout: {sys.stdout.encoding}")
    print(f"Codificación de stderr: {sys.stderr.encoding}")
    
    # Prueba de impresión con caracteres especiales
    print("Prueba de caracteres Unicode: áéíóú ñÑ €")
    
    return True

if __name__ == "__main__":
    print("Aplicando solución de codificación para consola...")
    fix_console_encoding()
    print("Configuración completada.")
