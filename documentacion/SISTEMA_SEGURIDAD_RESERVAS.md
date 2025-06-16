# Sistema de Seguridad de Reservas - Prevención de Abuso

## Problema Identificado

Durante la presentación del proyecto, se planteó la pregunta: **"¿Cómo controlas que un usuario no vaya reservando todas las salas de una vez? ¿Algún usuario malintencionado? ¿Qué soluciones se podrían proponer?"**

Esta es una preocupación válida y común en sistemas de reservas, donde usuarios malintencionados pueden:
- Hacer reservas masivas para monopolizar recursos
- Reservar y cancelar repetidamente para interrumpir el servicio
- Usar múltiples cuentas o IPs para evadir límites
- Hacer reservas falsas o especulativas

## Solución Implementada

Hemos implementado un **Sistema Integral de Seguridad de Reservas** que incluye múltiples capas de protección:

### 1. 🛡️ Límites por Rol de Usuario

**Descripción**: Diferentes límites según el rol del usuario en el sistema.

**Implementación**:
- **Estudiantes**: Límites restrictivos (2/hora, 5/día, 15/semana)
- **Profesores**: Límites moderados (5/hora, 10/día, 30/semana)
- **Administradores**: Límites altos con exenciones especiales
- **Por Defecto**: Límites básicos para usuarios sin rol específico

**Beneficios**:
- Uso diferenciado según necesidades reales
- Flexibilidad para diferentes tipos de usuarios
- Fácil configuración desde el panel de administración

### 2. ⏱️ Rate Limiting Multi-Nivel

**Descripción**: Control de frecuencia de solicitudes en múltiples ventanas de tiempo.

**Implementación**:
- Límites por **hora** (previene ráfagas de reservas)
- Límites por **día** (controla uso diario total)
- Límites por **semana** (evita acumulación semanal)
- Límites de **reservas simultáneas** activas

**Ejemplo para Estudiantes**:
```
- Máximo 2 reservas por hora
- Máximo 5 reservas por día
- Máximo 15 reservas por semana
- Máximo 2 reservas activas simultáneamente
```

### 3. 🔍 Detección de Patrones Abusivos

**Descripción**: Análisis inteligente de comportamiento para detectar actividad sospechosa.

**Patrones Detectados**:
- **Intentos masivos bloqueados**: Múltiples intentos fallidos
- **Cancelaciones rápidas**: Reservar y cancelar en menos de 5 minutos
- **Múltiples IPs**: Reservas desde diferentes direcciones IP
- **Horarios anómalos**: Patrones de uso inusuales

**Algoritmo**:
```python
def detect_suspicious_patterns(user):
    suspicions = []
    
    # Patrón 1: Muchos intentos bloqueados
    blocked_attempts = recent_logs.filter(action='attempt_blocked').count()
    if blocked_attempts >= 5:
        suspicions.append('excessive_blocked_attempts')
    
    # Patrón 2: Cancelaciones rápidas
    for reservation in recent_reservations:
        if cancelled_within_minutes(reservation, 5):
            suspicions.append('quick_cancellation_pattern')
    
    return suspicions
```

### 4. 🚫 Bloqueo Temporal Automático

**Descripción**: Suspensión automática de usuarios que violan límites repetidamente.

**Trigger Conditions**:
- Múltiples violaciones de límites (≥2 tipos diferentes)
- Patrones sospechosos de alta severidad
- Intentos consecutivos después de advertencias

**Duración del Bloqueo**:
- **Estudiantes**: 30 minutos
- **Profesores**: 60 minutos
- **Usuarios por defecto**: 60 minutos
- **Administradores**: Exentos

**Proceso**:
1. Detección de violación
2. Registro automático del evento
3. Bloqueo temporal en cache
4. Notificación automática a administradores
5. Liberación automática al expirar

### 5. 📊 Logging y Monitoreo Completo

**Descripción**: Registro detallado de todas las acciones para análisis y auditoría.

**Eventos Registrados**:
- `create`: Creación exitosa de reserva
- `cancel`: Cancelación de reserva
- `attempt_blocked`: Intento bloqueado por límites
- `warning_sent`: Advertencia enviada al usuario
- `user_blocked`: Usuario bloqueado temporalmente

**Información Capturada**:
```json
{
    "user": "username",
    "action": "attempt_blocked",
    "room_name": "Sala A",
    "timestamp": "2025-06-16T10:30:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "additional_data": {
        "violations": ["hourly_limit", "daily_limit"],
        "reason": "Multiple rate limits exceeded"
    }
}
```

### 6. 🌐 Rate Limiting por IP

**Descripción**: Protección adicional contra ataques automatizados desde la misma IP.

**Límites por IP**:
- **Reservas**: 10 por hora por IP
- **Login**: 20 por hora por IP
- **Registro**: 5 por hora por IP

**Implementación**:
```python
def check_rate_limit(ip_address, path):
    cache_key = f"ip_rate_limit_{ip_address}_{path}"
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        return False
    
    cache.set(cache_key, current_count + 1, timeout=3600)
    return True
```

### 7. ⚠️ Sistema de Advertencias

**Descripción**: Notificaciones proactivas cuando los usuarios se acercan a sus límites.

**Umbrales de Advertencia**:
- Se activan al 80% del límite establecido
- Mostradas en la interfaz de usuario
- Incluidas en respuestas AJAX

**Ejemplo**:
```
"Advertencia: Cerca del límite diario (4/5 reservas)"
```

## Arquitectura Técnica

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE SEGURIDAD                     │
├─────────────────────────────────────────────────────────────┤
│  1. ReservationSecurityMiddleware                           │
│     ├── Intercepta requests de reserva                     │
│     ├── Valida límites antes de procesar                   │
│     └── Registra intentos bloqueados                       │
│                                                             │
│  2. SecurityManager                                         │
│     ├── Validación de límites                              │
│     ├── Detección de patrones                              │
│     ├── Gestión de bloqueos                                │
│     └── Logging de eventos                                 │
│                                                             │
│  3. Base de Datos                                           │
│     ├── ReservationSecurityRule (Configuración)            │
│     └── ReservationUsageLog (Auditoría)                    │
│                                                             │
│  4. Cache Layer                                             │
│     ├── Bloqueos temporales                                │
│     ├── Rate limiting por IP                               │
│     └── Contadores de uso                                  │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Validación

```
Usuario intenta hacer reserva
         │
         ▼
¿Usuario bloqueado? ──Sí──► Rechazar (429 Too Many Requests)
         │
        No
         ▼
¿Límites excedidos? ──Sí──► Rechazar + Log + Posible Bloqueo
         │
        No
         ▼
¿Patrones sospechosos? ──Sí──► Advertencia + Monitoreo Extra
         │
        No
         ▼
Procesar Reserva Normal + Log Exitoso
```

## Configuración y Uso

### 1. Instalación

```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Inicializar reglas de seguridad
python manage.py init_reservation_security --verbose
```

### 2. Configuración en settings.py

```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'core.reservation_security_middleware.ReservationSecurityMiddleware',
    'core.reservation_security_middleware.RateLimitMiddleware',
]

# Cache para rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### 3. Administración

Acceder a **Admin > Core > Reglas de Seguridad de Reservas** para:
- Ajustar límites por rol
- Configurar duración de bloqueos
- Activar/desactivar detección de patrones
- Establecer umbrales de advertencia

### 4. Monitoreo

Revisar **Admin > Core > Logs de Uso de Reservas** para:
- Análisis de patrones de uso
- Identificación de usuarios problemáticos
- Estadísticas de violaciones
- Auditoría de seguridad

## Demostración del Sistema

### Script de Prueba

Ejecutar el script de demostración:

```bash
python scripts/demo_security_system.py
```

Este script simula:
- Intentos masivos de reserva
- Violaciones de límites
- Detección de patrones sospechosos
- Bloqueo temporal de usuario
- Generación de logs

### Casos de Prueba

1. **Reservas Masivas**: Intentar 10 reservas en 1 hora (límite: 2)
2. **Reservas Simultáneas**: Crear 5 reservas superpuestas (límite: 2)
3. **Patrones Sospechosos**: Generar múltiples intentos bloqueados
4. **Bloqueo Temporal**: Activar bloqueo y verificar restricciones

## Beneficios del Sistema

### Para los Usuarios Legítimos
- **Transparencia**: Información clara sobre límites y uso actual
- **Advertencias Proactivas**: Notificaciones antes de alcanzar límites
- **Uso Justo**: Garantiza acceso equitativo a recursos

### Para los Administradores
- **Control Granular**: Configuración flexible por rol de usuario
- **Monitoreo Completo**: Visibilidad total del uso del sistema
- **Respuesta Automática**: Prevención automática de abuso sin intervención manual
- **Análisis de Datos**: Estadísticas para optimizar políticas

### Para el Sistema
- **Protección Robusta**: Múltiples capas de seguridad
- **Escalabilidad**: Manejo eficiente de alta carga
- **Flexibilidad**: Fácil ajuste de parámetros según necesidades
- **Auditabilidad**: Registro completo para cumplimiento y análisis

## Casos de Uso Reales

### Escenario 1: Estudiante Malintencionado
**Situación**: Un estudiante intenta reservar todas las salas para un día específico.

**Protección**:
1. Después de 2 reservas en 1 hora → Bloqueado temporalmente
2. Sistema detecta patrón de intentos masivos
3. Administradores reciben alerta automática
4. Usuario bloqueado por 30 minutos

### Escenario 2: Bot Automatizado
**Situación**: Script automatizado hace múltiples requests desde la misma IP.

**Protección**:
1. Rate limiting por IP (10/hora) se activa
2. Requests adicionales retornan 429 Too Many Requests
3. Sistema registra actividad sospechosa
4. IP bloqueada temporalmente

### Escenario 3: Uso Legítimo Intensivo
**Situación**: Profesor necesita hacer múltiples reservas para evento académico.

**Protección**:
1. Límites más altos para rol "profesor" (5/hora, 10/día)
2. Advertencias al 80% del límite
3. Posibilidad de solicitar exención temporal
4. Monitoreo sin bloqueo automático

## Futuras Mejoras

### Corto Plazo
- [ ] Dashboard de estadísticas en tiempo real
- [ ] Alertas por email/SMS para administradores
- [ ] API REST para integración externa
- [ ] Reportes automáticos de actividad

### Mediano Plazo
- [ ] Machine Learning para detección de anomalías
- [ ] Integración con sistemas de autenticación externa
- [ ] Whitelist/blacklist de IPs
- [ ] Análisis predictivo de demanda

### Largo Plazo
- [ ] Sistema de reputación de usuarios
- [ ] Algoritmos adaptativos de límites
- [ ] Integración con sistemas de videovigilancia
- [ ] Blockchain para auditoría inmutable

## Conclusión

El sistema implementado proporciona una **solución robusta y escalable** para prevenir el abuso en sistemas de reservas. Combina:

✅ **Prevención Proactiva**: Límites y validaciones antes de problemas  
✅ **Detección Inteligente**: Análisis de patrones de comportamiento  
✅ **Respuesta Automática**: Bloqueos y alertas sin intervención manual  
✅ **Flexibilidad**: Configuración adaptable a diferentes necesidades  
✅ **Transparencia**: Información clara para usuarios y administradores  

Este enfoque multicapa asegura que los recursos del sistema estén disponibles de manera equitativa para todos los usuarios legítimos, mientras se protege eficazmente contra comportamientos abusivos o malintencionados.

---

**Fecha de Implementación**: Junio 2025  
**Versión**: 1.0  
**Estado**: Producción Ready  
**Contacto**: Equipo de Desarrollo - Proyecto Calidad
