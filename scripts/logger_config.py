"""
Módulo de configuración de logging para scripts
que asegura el manejo correcto de caracteres Unicode.
"""

import os
import sys
import logging
import io
import platform

def setup_script_logging(name):
    """
    Configura el logging para scripts, maneja correctamente caracteres Unicode en consola.
    
    Args:
        name (str): Nombre del logger a configurar
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Eliminar handlers existentes si hay
    if logger.handlers:
        logger.handlers = []
    
    # Formato de log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Añadir handler al logger
    logger.addHandler(console_handler)
    
    # Handler para archivo de log si estamos en un entorno de desarrollo
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            pass  # Si no podemos crear el directorio, simplemente no loguearemos a archivo
    
    if os.path.exists(log_dir):
        log_file = os.path.join(log_dir, f"{name}.log")
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # Si hay algún problema con el archivo, continuamos sin él
    
    return logger

if __name__ == "__main__":
    # Prueba de la función
    logger = setup_script_logging("test_logger")
    logger.info("Probando caracteres Unicode: áéíóú ñÑ €")
