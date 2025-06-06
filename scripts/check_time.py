"""
Script para verificar zona horaria.
"""
import os
import datetime
import pytz

# Mostrar hora actual del sistema
print(f"Hora actual del sistema: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Mostrar hora en UTC
utc_now = datetime.datetime.now(pytz.UTC)
print(f"Hora actual UTC: {utc_now.strftime('%d/%m/%Y %H:%M:%S')}")

# Mostrar hora en Santiago de Chile
cl_tz = pytz.timezone('America/Santiago')
cl_now = datetime.datetime.now(cl_tz)
print(f"Hora actual Chile: {cl_now.strftime('%d/%m/%Y %H:%M:%S')}")
