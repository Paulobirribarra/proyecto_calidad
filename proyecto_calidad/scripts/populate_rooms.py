# -*- coding: utf-8 -*-
"""
Script para poblar la base de datos con salas de diferentes tipos.

Este script crea salas de estudio de distintos tipos con diferentes permisos
según los roles definidos en el sistema.

Se debe ejecutar con: python manage.py shell < populate_rooms.py
"""

import os
import django
import random
import unicodedata

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_calidad.settings')
django.setup()

# Importar después de configurar Django
from django.contrib.auth import get_user_model
from rooms.models import Room
from django.utils import timezone
from datetime import time, timedelta

User = get_user_model()

# Datos para generar salas
UBICACIONES = [
    'Edificio Central - Planta 1', 'Edificio Central - Planta 2',
    'Biblioteca - Zona Sur', 'Biblioteca - Zona Norte',
    'Pabellón de Ciencias - Planta Baja', 'Pabellón de Ciencias - Planta Alta',
    'Campus Norte - Edificio A', 'Campus Norte - Edificio B',
    'Campus Sur - Edificio C', 'Facultad de Ingeniería - Sector 1',
    'Facultad de Letras - Aula Magna', 'Centro de Estudios - Planta 3'
]

EQUIPOS = [
    'Proyector, pizarra blanca, marcadores',
    'Computadores (10), proyector, equipo de sonido',
    'Pizarra interactiva, proyector, webcam HD',
    'Mesa de conferencia, proyector, sistema de videoconferencia',
    'Pizarra blanca, cámaras de documentos',
    'Pantalla táctil, sistema de audio, micrófonos inalámbricos',
    'Proyector 4K, sistema de sonido Dolby',
    'Pizarra tradicional, proyector básico',
    'Pizarras blancas móviles (3), proyector LED',
    'Ordenador profesor, proyector, altavoces'
]

def normalizar(texto):
    # Normaliza a NFC y elimina caracteres problemáticos
    if isinstance(texto, str):
        return unicodedata.normalize('NFC', texto)
    return texto

def crear_salas():
    """Crea salas de diferentes tipos con distintos permisos"""
    
    # Obtener un usuario administrador para asignarlo como creador
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        # Si no hay admin, tomar el primer usuario
        admin_user = User.objects.first()
    
    # Definir tipos de salas y sus permisos
    tipos_salas = [
        {
            'tipo': 'aula',
            'permisos': 'admin,profesor',
            'nombres': [normalizar(n) for n in ['Aula Magna', 'Aula 101', 'Aula 102', 'Aula 201', 'Aula 202']]
        },
        {
            'tipo': 'sala_estudio',
            'permisos': 'admin,profesor,estudiante',
            'nombres': [normalizar(n) for n in ['Sala de Estudio 1', 'Sala de Estudio 2', 'Sala Grupal A', 'Sala Grupal B']]
        },
        {
            'tipo': 'sala_individual',
            'permisos': 'admin,profesor,estudiante',
            'nombres': [normalizar(n) for n in ['Cúbiculo 1', 'Cúbiculo 2', 'Cúbiculo 3', 'Espacio Individual A']]
        },
        {
            'tipo': 'sala_reunion',  # sin tilde
            'permisos': 'admin,profesor,soporte',
            'nombres': [normalizar(n) for n in ['Sala de Juntas', 'Sala de Reuniones 1', 'Sala de Conferencias']]
        },
        {
            'tipo': 'laboratorio',
            'permisos': 'admin,profesor',
            'nombres': [normalizar(n) for n in ['Laboratorio de Informática', 'Laboratorio de Ciencias', 'Laboratorio de Idiomas']]
        },
        {
            'tipo': 'auditorio',
            'permisos': 'admin,profesor',
            'nombres': [normalizar(n) for n in ['Auditorio Principal', 'Salón de Actos', 'Auditorio de Ciencias']]
        }
    ]
    
    salas_creadas = []
    print("Creando salas...")
    
    for tipo_sala in tipos_salas:
        for nombre in tipo_sala['nombres']:
            # Verificar si ya existe
            if Room.objects.filter(name=nombre).exists():
                print(f"La sala '{nombre}' ya existe, omitiendo...")
                continue
            
            # Valores aleatorios
            capacidad = random.randint(5, 100)
            if tipo_sala['tipo'] == 'sala_individual':
                capacidad = random.randint(1, 4)  # Las salas individuales son pequeñas
                
            ubicacion = random.choice(UBICACIONES)
            equipo = random.choice(EQUIPOS)
            
            # Horario aleatorios dentro de rangos razonables
            hora_apertura = time(7 + random.randint(0, 3), 0)  # Entre 7:00 y 10:00
            hora_cierre = time(19 + random.randint(0, 3), 0)   # Entre 19:00 y 22:00
            # Tasa por hora según tipo de sala (precios más realistas)
            if tipo_sala['tipo'] in ['auditorio', 'laboratorio']:
                tasa = random.randint(15000, 25000)  # $15.000 - $25.000 por hora
            elif tipo_sala['tipo'] in ['sala_reunion', 'aula']:
                tasa = random.randint(8000, 15000)   # $8.000 - $15.000 por hora
            elif tipo_sala['tipo'] in ['sala_estudio', 'sala_individual']:
                tasa = 0  # Gratuitas para estudiantes
            else:
                tasa = random.randint(5000, 12000)   # $5.000 - $12.000 por hora
                
            try:
                sala = Room.objects.create(
                    name=normalizar(nombre),
                    description=normalizar(f"Sala tipo {tipo_sala['tipo']} ubicada en {normalizar(ubicacion)}. " +
                            f"Ideal para {capacidad} personas. " +
                            f"Cuenta con el siguiente equipamiento: {normalizar(equipo)}."),
                    capacity=capacidad,
                    equipment=normalizar(equipo),
                    location=normalizar(ubicacion),
                    is_active=True,
                    hourly_rate=float(tasa),
                    opening_time=hora_apertura,
                    closing_time=hora_cierre,
                    room_type=tipo_sala['tipo'],
                    allowed_roles=tipo_sala['permisos'],
                    created_by=admin_user
                )
                
                salas_creadas.append(sala)
                print(f"Sala creada: {nombre} - Tipo: {tipo_sala['tipo']} - Roles: {tipo_sala['permisos']}")
            except Exception as e:
                print(f"Error al crear sala {nombre}: {e}")
    
    return salas_creadas

# Ejecutar automáticamente al importar
print(f"Salas existentes: {Room.objects.count()}")

# Crear salas
salas = crear_salas()

# Mostrar resumen
print(f"\nTotal de salas creadas: {len(salas)}")

# Mostrar estadísticas por tipo de sala
tipos = Room.objects.values_list('room_type').distinct()

print("\nDistribución por tipo de sala:")
for tipo in tipos:
    count = Room.objects.filter(room_type=tipo[0]).count()
    print(f"- {tipo[0]}: {count} salas")