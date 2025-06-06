# Manual de Usuario - Sistema de Reserva de Salas

## Índice
1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Roles de Usuario](#roles-de-usuario)
4. [Navegación Principal](#navegación-principal)
5. [Búsqueda y Filtrado de Salas](#búsqueda-y-filtrado-de-salas)
6. [Reservar una Sala](#reservar-una-sala)
7. [Gestión de Reservas](#gestión-de-reservas)
8. [Calificación de Salas](#calificación-de-salas)
9. [Panel de Administración](#panel-de-administración)
10. [Preguntas Frecuentes](#preguntas-frecuentes)
11. [Resolución de Problemas](#resolución-de-problemas)

---

## Introducción

### ¿Qué es el Sistema de Reserva de Salas?
El Sistema de Reserva de Salas es una plataforma web diseñada para facilitar la reserva y gestión de espacios de estudio y trabajo en instituciones educativas. Permite a estudiantes, profesores y personal administrativo reservar salas de manera eficiente y organizada.

### Funcionalidades Principales
- ✅ Búsqueda y filtrado de salas disponibles
- ✅ Reserva de salas en tiempo real
- ✅ Gestión de reservas personales
- ✅ Sistema de calificaciones y reseñas
- ✅ Panel administrativo para gestión de salas
- ✅ Control de acceso basado en roles

### Beneficios
- **Eficiencia**: Reserva salas en segundos
- **Transparencia**: Ve la disponibilidad en tiempo real
- **Organización**: Gestiona todas tus reservas desde un lugar
- **Calidad**: Sistema de calificaciones para mejorar el servicio

---

## Acceso al Sistema

### Registro de Cuenta

1. **Visitar la página de registro**
   - Ir a la URL del sistema
   - Hacer clic en "Registrarse"

2. **Completar el formulario**
   - **Nombre de usuario**: Único en el sistema
   - **Email**: Dirección de correo válida
   - **Nombre y apellido**: Información personal
   - **Contraseña**: Mínimo 8 caracteres
   - **Tipo de usuario**: Seleccionar rol apropiado

3. **Confirmar registro**
   - Revisar la información
   - Hacer clic en "Crear cuenta"

### Inicio de Sesión

1. **Acceder al sistema**
   - Ir a la página principal
   - Hacer clic en "Iniciar Sesión"

2. **Introducir credenciales**
   - Nombre de usuario o email
   - Contraseña

3. **Confirmar acceso**
   - Hacer clic en "Entrar"
   - Será redirigido al panel principal

### Recuperación de Contraseña

1. **Solicitar restablecimiento**
   - En la página de login, hacer clic en "¿Olvidaste tu contraseña?"
   - Introducir email o nombre de usuario

2. **Seguir instrucciones**
   - Revisar correo electrónico
   - Seguir el enlace recibido
   - Establecer nueva contraseña

---

## Roles de Usuario

### 👨‍🎓 Estudiante
**Permisos:**
- Reservar salas de estudio y salas individuales
- Ver salas gratuitas
- Gestionar sus propias reservas
- Calificar salas utilizadas

**Limitaciones:**
- No puede acceder a laboratorios especializados
- No puede reservar auditorios
- Limitado a salas de bajo costo

### 👨‍🏫 Profesor
**Permisos:**
- Reservar todas las salas excepto salas de servidor
- Acceso a laboratorios y aulas especializadas
- Gestionar reservas de grupo
- Reservar auditorios para conferencias

**Limitaciones:**
- No puede acceder a salas de servidor
- No puede crear nuevas salas

### 👨‍💼 Administrador
**Permisos:**
- Acceso completo al sistema
- Crear, editar y eliminar salas
- Ver todas las reservas del sistema
- Gestionar usuarios
- Acceso al panel administrativo

**Responsabilidades:**
- Mantener el sistema actualizado
- Resolver conflictos de reservas
- Supervisar el uso del sistema

### 🔧 Soporte Técnico
**Permisos:**
- Reservar salas técnicas y laboratorios
- Acceso a salas de equipamiento especializado
- Gestionar mantenimiento de salas

**Limitaciones:**
- No puede crear usuarios
- No puede eliminar salas

---

## Navegación Principal

### Barra de Navegación Superior
```
[Logo] Salas | Mis Reservas | [Usuario] ▼
```

#### Menú Principal
- **Salas**: Lista todas las salas disponibles
- **Mis Reservas**: Gestiona tus reservas personales
- **Perfil**: Configuración de cuenta personal

#### Menú de Usuario (Desplegable)
- **Mi Perfil**: Editar información personal
- **Mis Reservas**: Acceso rápido a reservas
- **Configuración**: Preferencias del sistema
- **Cerrar Sesión**: Salir del sistema

### Panel Principal (Dashboard)

#### Para Estudiantes
```
┌─────────────────────────────────────┐
│  🏠 Bienvenido, [Nombre]            │
│  📊 Estadísticas Rápidas            │
│  • Reservas activas: X              │
│  • Próximas reservas: X             │
│  • Salas favoritas: X               │
│                                     │
│  🔍 Búsqueda Rápida                 │
│  [Buscar salas...]      [Buscar]    │
│                                     │
│  ⭐ Acciones Rápidas                │
│  [Nueva Reserva] [Mis Reservas]     │
└─────────────────────────────────────┘
```

#### Para Administradores
```
┌─────────────────────────────────────┐
│  🏠 Panel de Administración         │
│  📊 Estadísticas del Sistema        │
│  • Total salas: X                   │
│  • Reservas hoy: X                  │
│  • Usuarios activos: X              │
│                                     │
│  🛠️ Herramientas Admin             │
│  [Crear Sala] [Gestionar Usuarios]  │
│  [Ver Reportes] [Configuración]     │
└─────────────────────────────────────┘
```

---

## Búsqueda y Filtrado de Salas

### Acceso a la Lista de Salas
1. **Navegación**
   - Hacer clic en "Salas" en el menú principal
   - O usar el botón "Nueva Reserva" desde el dashboard

### Filtros Disponibles

#### 🔍 Búsqueda por Texto
- **Campo**: "Buscar por nombre"
- **Función**: Busca en nombre, ubicación y descripción
- **Ejemplo**: "Laboratorio", "Piso 2", "Proyector"

#### 👥 Capacidad Mínima
- **Campo**: "Capacidad mínima"
- **Función**: Filtra salas con al menos X personas
- **Rango**: 1-100 personas

#### 🎭 Filtro por Rol
- **Automático**: Basado en tu tipo de usuario
- **Manual**: Puedes ver salas disponibles para otros roles
- **Opciones**: Estudiante, Profesor, Administrador, Soporte

#### 🏢 Tipo de Sala
- **Sala de Estudio**: Espacios para estudio individual o grupal
- **Laboratorio**: Espacios con equipamiento especializado
- **Aula Magna**: Espacios grandes para conferencias
- **Sala de Reuniones**: Espacios para reuniones profesionales
- **Auditorio**: Espacios para eventos grandes

#### ⏰ Disponibilidad
- **Disponible Ahora**: Salas libres en este momento
- **Disponible Hoy**: Salas con tiempo libre hoy
- **Horario Específico**: Para una fecha/hora particular

### Cómo Usar los Filtros

1. **Aplicar filtros**
   ```
   ┌─────────────────────────────────────┐
   │ 🔍 Buscar por nombre                │
   │ [Laboratorio...]                    │
   │                                     │
   │ 👥 Capacidad mínima: [20] personas  │
   │                                     │
   │ 🎭 Filtrar por rol: [Profesor] ▼    │
   │                                     │
   │ ⏰ Disponibilidad: [Hoy] ▼          │
   │                                     │
   │ [Buscar Salas]                      │
   └─────────────────────────────────────┘
   ```

2. **Ver resultados**
   - Los resultados se actualizan automáticamente
   - Verás tarjetas con información de cada sala
   - Puedes ordenar por nombre, capacidad o disponibilidad

### Información de Cada Sala

#### Tarjeta de Sala
```
┌─────────────────────────────────────┐
│ 📍 Laboratorio de Informática A     │
│ 🏢 Edificio Tecnológico, Piso 2     │
│ 👥 Capacidad: 30 personas           │
│ 💰 $25/hora                         │
│ ⏰ 08:00 - 20:00                     │
│                                     │
│ 🛠️ Equipamiento:                    │
│ • 30 Computadoras                   │
│ • Proyector                         │
│ • Aire Acondicionado                │
│                                     │
│ 🟢 Disponible                       │
│ [Ver Detalles] [Reservar]           │
└─────────────────────────────────────┘
```

---

## Reservar una Sala

### Proceso de Reserva

#### Paso 1: Seleccionar Sala
1. **Buscar sala deseada**
   - Usar filtros para encontrar la sala ideal
   - Revisar disponibilidad y equipamiento

2. **Ver detalles**
   - Hacer clic en "Ver Detalles"
   - Revisar información completa
   - Ver horarios disponibles

#### Paso 2: Formulario de Reserva
1. **Acceder al formulario**
   - Hacer clic en "Reservar" desde la lista
   - O "Reservar Ahora" desde los detalles

2. **Completar información requerida**
   ```
   ┌─────────────────────────────────────┐
   │ 📅 Reservar: Laboratorio Info A     │
   │                                     │
   │ 📅 Fecha y Hora de Inicio *         │
   │ [2025-06-04] [14:00]                │
   │                                     │
   │ ⏰ Fecha y Hora de Fin *             │
   │ [2025-06-04] [16:00]                │
   │                                     │
   │ 🎯 Propósito de la Reserva *        │
   │ [Práctica de programación...]       │
   │                                     │
   │ 👥 Número de Asistentes *           │
   │ [25] personas                       │
   │ ℹ️ Máximo: 30 personas              │
   │                                     │
   │ 📝 Notas Adicionales                │
   │ [Información adicional...]          │
   │                                     │
   │ [Confirmar Reserva] [Cancelar]      │
   └─────────────────────────────────────┘
   ```

#### Paso 3: Validación y Confirmación
1. **Validaciones automáticas**
   - ✅ Horario dentro del funcionamiento de la sala
   - ✅ No conflicto con otras reservas
   - ✅ Número de asistentes dentro de la capacidad
   - ✅ Duración entre 30 minutos y 8 horas

2. **Información de la reserva**
   ```
   ┌─────────────────────────────────────┐
   │ ℹ️ Información de la Reserva        │
   │                                     │
   │ Duración: 2.0 horas                 │
   │ Costo Total: $50                    │
   │                                     │
   │ ⚠️ Política de Cancelación          │
   │ Puedes cancelar hasta 30 minutos    │
   │ antes del inicio.                   │
   └─────────────────────────────────────┘
   ```

3. **Confirmación**
   - Revisar todos los datos
   - Hacer clic en "Confirmar Reserva"
   - Recibir confirmación en pantalla

### Limitaciones por Número de Asistentes

#### Validación de Campo
- **Mínimo**: 1 persona
- **Máximo**: Capacidad de la sala
- **Límite de dígitos**: Máximo 4 dígitos (hasta 9999)
- **Solo números**: No se permiten caracteres especiales

#### Ejemplo de Validación en Tiempo Real
```
👥 Número de Asistentes: [9999] ✅
👥 Número de Asistentes: [10000] ❌ Máximo 4 dígitos
👥 Número de Asistentes: [abc] ❌ Solo números
👥 Número de Asistentes: [35] ❌ Excede capacidad (30)
```

### Información Importante
- **Anticipación**: Máximo 30 días de anticipación
- **Duración**: Entre 30 minutos y 8 horas
- **Cancelación**: Hasta 30 minutos antes del inicio
- **Modificación**: No disponible, debe cancelar y crear nueva

---

## Gestión de Reservas

### Acceso a Mis Reservas
1. **Navegación**
   - Hacer clic en "Mis Reservas" en el menú
   - O desde el dashboard personal

### Vista de Lista de Reservas

```
┌─────────────────────────────────────┐
│ 📅 Mis Reservas                     │
│                                     │
│ Filtrar por estado: [Todas] ▼       │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 🟢 Confirmada                   │ │
│ │ 📍 Lab Informática A            │ │
│ │ 📅 04/06/2025                   │ │
│ │ ⏰ 14:00 - 16:00                │ │
│ │ 👥 25 personas                  │ │
│ │                                 │ │
│ │ [Ver Detalles] [Cancelar]       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 🔴 Completada                   │ │
│ │ 📍 Sala Estudio B               │ │
│ │ 📅 02/06/2025                   │ │
│ │ ⏰ 10:00 - 12:00                │ │
│ │ 👥 5 personas                   │ │
│ │                                 │ │
│ │ [Ver Detalles] [Calificar]      │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Estados de Reserva

#### 🟢 Confirmada
- **Descripción**: Reserva activa y válida
- **Acciones disponibles**:
  - Ver detalles completos
  - Cancelar (hasta 30 min antes)
  - Descargar confirmación

#### 🟡 Pendiente
- **Descripción**: Esperando confirmación administrativa
- **Acciones disponibles**:
  - Ver detalles
  - Cancelar solicitud

#### 🔴 Cancelada
- **Descripción**: Reserva cancelada por usuario o sistema
- **Acciones disponibles**:
  - Ver detalles
  - Ver motivo de cancelación

#### ✅ Completada
- **Descripción**: Reserva finalizada exitosamente
- **Acciones disponibles**:
  - Ver detalles
  - Calificar sala (si no se ha hecho)

### Detalles de Reserva

#### Información Completa
```
┌─────────────────────────────────────┐
│ 📋 Detalle de Reserva #1234         │
│                                     │
│ 🏢 Información de la Sala           │
│ • Nombre: Laboratorio Informática A │
│ • Ubicación: Edificio Tech, Piso 2  │
│ • Capacidad: 30 personas            │
│ • Tipo: Laboratorio                 │
│                                     │
│ 📅 Detalles de la Reserva           │
│ • Fecha: Miércoles, 04 de Junio     │
│ • Horario: 14:00 - 16:00            │
│ • Duración: 2.0 horas               │
│ • Asistentes: 25 personas           │
│ • Reservado por: Juan Pérez         │
│                                     │
│ 🎯 Propósito                        │
│ Práctica de programación Java       │
│                                     │
│ 📝 Notas                            │
│ Necesitaremos proyector             │
│                                     │
│ ⏰ Estado: Confirmada               │
│ 🆔 ID de Reserva: RES-2025-001234   │
│ 📅 Creada: 01/06/2025 09:30         │
│                                     │
│ [Volver] [Cancelar Reserva]         │
└─────────────────────────────────────┘
```

### Cancelación de Reserva

#### Proceso de Cancelación
1. **Verificar tiempo límite**
   - Solo hasta 30 minutos antes del inicio
   - El sistema muestra tiempo restante

2. **Confirmar cancelación**
   ```
   ┌─────────────────────────────────────┐
   │ ⚠️ Confirmar Cancelación            │
   │                                     │
   │ ¿Estás seguro de que deseas         │
   │ cancelar la reserva de              │
   │ Laboratorio Informática A?          │
   │                                     │
   │ 📅 04/06/2025 14:00 - 16:00         │
   │                                     │
   │ ⚠️ Esta acción no se puede deshacer │
   │                                     │
   │ [No, mantener] [Sí, cancelar]       │
   └─────────────────────────────────────┘
   ```

3. **Confirmación de cancelación**
   - Mensaje de éxito
   - La sala queda disponible inmediatamente
   - Actualización del estado de la reserva

---

## Calificación de Salas

### Cuándo Calificar
- **Requisito**: Reserva completada exitosamente
- **Tiempo**: Después de que termine la reserva
- **Frecuencia**: Una vez por reserva

### Acceso a Calificación
1. **Desde Mis Reservas**
   - Buscar reserva con estado "Completada"
   - Hacer clic en "Calificar"

2. **Desde notificación**
   - El sistema puede enviar recordatorios
   - Hacer clic en el enlace directo

### Formulario de Calificación

```
┌─────────────────────────────────────┐
│ ⭐ Calificar: Lab Informática A     │
│                                     │
│ 📊 Calificación General             │
│ ⭐⭐⭐⭐⭐ (5 estrellas)            │
│                                     │
│ 🧹 Limpieza                         │
│ ⭐⭐⭐⭐⭐ (5 estrellas)            │
│                                     │
│ 🛠️ Equipamiento                     │
│ ⭐⭐⭐⭐⭐ (5 estrellas)            │
│                                     │
│ 🪑 Comodidad                        │
│ ⭐⭐⭐⭐⭐ (5 estrellas)            │
│                                     │
│ 💬 Tipo de Comentario               │
│ [Positivo] ▼                        │
│                                     │
│ 📝 Comentario                       │
│ ┌─────────────────────────────────┐ │
│ │ Excelente laboratorio, muy      │ │
│ │ bien equipado y limpio. Los     │ │
│ │ computadores funcionan          │ │
│ │ perfectamente.                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Enviar Calificación] [Cancelar]    │
└─────────────────────────────────────┘
```

#### Criterios de Calificación

**⭐ Calificación General (1-5 estrellas)**
- 1 ⭐: Muy malo
- 2 ⭐⭐: Malo
- 3 ⭐⭐⭐: Regular
- 4 ⭐⭐⭐⭐: Bueno
- 5 ⭐⭐⭐⭐⭐: Excelente

**🧹 Limpieza**
- Estado general de limpieza
- Mantenimiento del espacio
- Condiciones higiénicas

**🛠️ Equipamiento**
- Funcionamiento de equipos
- Disponibilidad de herramientas
- Estado de mobiliario

**🪑 Comodidad**
- Confort del espacio
- Temperatura ambiente
- Ruido y distracciones

#### Tipos de Comentario
- **Positivo**: Experiencia satisfactoria
- **Neutral**: Experiencia promedio
- **Negativo**: Problemas o sugerencias
- **Sugerencia**: Propuestas de mejora

### Beneficios de Calificar
- 📈 **Mejora del servicio**: Tu opinión ayuda a mejorar
- 🎯 **Mejor selección**: Ayudas a otros usuarios
- 🏆 **Reconocimiento**: Las mejores salas se destacan
- 📊 **Estadísticas**: Contribuyes a datos del sistema

---

## Panel de Administración

*Nota: Esta sección es solo para usuarios con rol de Administrador*

### Acceso al Panel Admin
1. **Desde el menú principal**
   - Hacer clic en el ícono de configuración
   - Seleccionar "Panel de Administración"

2. **URL directa**
   - Navegar a `/admin/`
   - Iniciar sesión con credenciales de administrador

### Gestión de Salas

#### Crear Nueva Sala
```
┌─────────────────────────────────────┐
│ 🏢 Crear Nueva Sala                 │
│                                     │
│ 📝 Información Básica               │
│ • Nombre: [________________________] │
│ • Ubicación: [____________________] │
│ • Descripción: [__________________] │
│                                     │
│ 👥 Capacidad y Horarios             │
│ • Capacidad: [___] personas         │
│ • Hora apertura: [08:00]            │
│ • Hora cierre: [20:00]              │
│ • Tarifa/hora: $[____]              │
│                                     │
│ 🏷️ Configuración                    │
│ • Tipo de sala: [Laboratorio] ▼     │
│ • Roles permitidos: [☑] Estudiante  │
│                     [☑] Profesor    │
│                     [☑] Admin       │
│                                     │
│ 🛠️ Equipamiento                     │
│ ┌─────────────────────────────────┐ │
│ │ Computadoras, Proyector,        │ │
│ │ Aire acondicionado, WiFi        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Crear Sala] [Cancelar]             │
└─────────────────────────────────────┘
```

#### Editar Sala Existente
1. **Seleccionar sala**
   - Ir a lista de salas en admin
   - Hacer clic en la sala a editar

2. **Modificar información**
   - Cambiar cualquier campo necesario
   - Guardar cambios

3. **Consideraciones**
   - Verificar impacto en reservas existentes
   - Notificar cambios importantes a usuarios

### Gestión de Reservas

#### Ver Todas las Reservas
- **Filtros disponibles**:
  - Por fecha
  - Por estado
  - Por usuario
  - Por sala

#### Modificar Reservas
- **Cambiar estado**: Confirmar, cancelar, completar
- **Editar detalles**: Horarios, notas administrativas
- **Resolver conflictos**: Manejar solapamientos

### Gestión de Usuarios

#### Ver Lista de Usuarios
```
┌─────────────────────────────────────┐
│ 👥 Gestión de Usuarios              │
│                                     │
│ Buscar: [________________] [🔍]      │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 👨‍🎓 juan.perez                   │ │
│ │ ✉️ juan@email.com                │ │
│ │ 🎭 Estudiante                    │ │
│ │ 📅 Activo desde: 01/01/2025     │ │
│ │ [Editar] [Desactivar]           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 👨‍🏫 maria.garcia                 │ │
│ │ ✉️ maria@email.com               │ │
│ │ 🎭 Profesor                      │ │
│ │ 📅 Activo desde: 15/12/2024     │ │
│ │ [Editar] [Desactivar]           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### Acciones de Usuario
- **Editar perfil**: Cambiar información personal
- **Cambiar rol**: Asignar diferentes permisos
- **Desactivar cuenta**: Suspender acceso temporalmente
- **Ver actividad**: Historial de reservas y acciones

### Reportes y Estadísticas

#### Dashboard de Administración
```
┌─────────────────────────────────────┐
│ 📊 Estadísticas del Sistema         │
│                                     │
│ 📈 Hoy                              │
│ • Reservas activas: 45              │
│ • Nuevas reservas: 12               │
│ • Cancelaciones: 3                  │
│                                     │
│ 📊 Esta Semana                      │
│ • Total reservas: 234               │
│ • Tasa ocupación: 78%               │
│ • Satisfacción promedio: 4.2/5      │
│                                     │
│ 🏆 Salas Más Populares             │
│ 1. Lab Informática A (45 reservas) │
│ 2. Sala Estudio B (38 reservas)    │
│ 3. Auditorio Principal (22 reservas)│
│                                     │
│ [Ver Reporte Completo]              │
└─────────────────────────────────────┘
```

---

## Preguntas Frecuentes

### ❓ Reservas

**P: ¿Con cuánta anticipación puedo reservar una sala?**
R: Puedes reservar con hasta 30 días de anticipación. No puedes reservar para fechas pasadas.

**P: ¿Cuál es la duración mínima y máxima de una reserva?**
R: La duración mínima es de 30 minutos y la máxima es de 8 horas continuas.

**P: ¿Puedo modificar una reserva existente?**
R: No es posible modificar reservas. Debes cancelar la existente y crear una nueva.

**P: ¿Hasta cuándo puedo cancelar una reserva?**
R: Puedes cancelar hasta 30 minutos antes del horario de inicio.

### ❓ Acceso y Permisos

**P: ¿Por qué no puedo reservar ciertas salas?**
R: El acceso a salas está restringido por tipo de usuario:
- Estudiantes: Solo salas de estudio e individuales
- Profesores: Todas excepto salas de servidor
- Administradores: Acceso completo

**P: ¿Cómo cambio mi tipo de usuario?**
R: Solo los administradores pueden cambiar roles. Contacta al soporte técnico.

**P: ¿Qué hago si olvido mi contraseña?**
R: Usa la opción "¿Olvidaste tu contraseña?" en la página de inicio de sesión.

### ❓ Problemas Técnicos

**P: ¿Qué hago si el sistema está lento?**
R: 
1. Actualiza la página (F5)
2. Limpia caché del navegador
3. Verifica tu conexión a internet
4. Contacta soporte si persiste

**P: ¿Por qué no aparece mi reserva?**
R: 
1. Verifica que la reserva se confirmó correctamente
2. Revisa el estado en "Mis Reservas"
3. Contacta soporte con el ID de reserva

**P: ¿El sistema funciona en móviles?**
R: Sí, el sistema es completamente responsive y funciona en dispositivos móviles.

### ❓ Calificaciones

**P: ¿Cuándo puedo calificar una sala?**
R: Solo después de que termine la reserva y cambie al estado "Completada".

**P: ¿Puedo cambiar mi calificación?**
R: No, las calificaciones son finales. Asegúrate antes de enviar.

**P: ¿Son anónimas las calificaciones?**
R: Las calificaciones son asociadas a tu usuario pero solo los administradores pueden ver quién calificó.

---

## Resolución de Problemas

### 🔧 Problemas Comunes

#### No Puedo Iniciar Sesión
**Síntomas**: Error al introducir credenciales
**Soluciones**:
1. ✅ Verificar nombre de usuario y contraseña
2. ✅ Verificar que la cuenta esté activa
3. ✅ Intentar con email en lugar de usuario
4. ✅ Usar recuperación de contraseña
5. ✅ Limpiar cookies del navegador

#### La Página Se Carga Lentamente
**Síntomas**: Demora en cargar contenido
**Soluciones**:
1. ✅ Verificar conexión a internet
2. ✅ Cerrar otras pestañas del navegador
3. ✅ Limpiar caché del navegador
4. ✅ Probar en modo incógnito
5. ✅ Contactar soporte técnico

#### Error al Crear Reserva
**Síntomas**: Mensaje de error al confirmar reserva
**Soluciones**:
1. ✅ Verificar que todos los campos están completos
2. ✅ Comprobar que la fecha es válida (futuro)
3. ✅ Verificar que el número de asistentes es correcto
4. ✅ Asegurar que no hay conflicto de horarios
5. ✅ Intentar con otra sala similar

#### No Veo Mis Reservas
**Síntomas**: Lista de reservas aparece vacía
**Soluciones**:
1. ✅ Verificar filtros aplicados
2. ✅ Cambiar filtro a "Todas las reservas"
3. ✅ Verificar que tienes reservas creadas
4. ✅ Refrescar la página
5. ✅ Contactar soporte con tu usuario

### 🆘 Contacto de Soporte

#### Información Necesaria para Soporte
Cuando contactes soporte, incluye:
- **Usuario**: Tu nombre de usuario
- **Fecha y hora**: Cuándo ocurrió el problema
- **Navegador**: Chrome, Firefox, Safari, etc.
- **Descripción**: Qué intentabas hacer
- **Error**: Mensaje de error específico
- **Pasos**: Qué pasos seguiste

#### Canales de Soporte
- **Email**: soporte@sistema-salas.com
- **Teléfono**: +1-234-567-8900 (Lun-Vie 9:00-17:00)
- **Formulario**: Desde el sistema, menú "Ayuda"
- **Documentación**: DOCUMENTACION_TECNICA.md

#### Tiempos de Respuesta
- **Crítico**: 2 horas (sistema inaccesible)
- **Alto**: 4 horas (funcionalidad principal afectada)
- **Medio**: 1 día laboral (problema menor)
- **Bajo**: 3 días laborales (mejora o consulta)

### 🔍 Códigos de Error Comunes

#### E001: Credenciales Inválidas
- **Causa**: Usuario o contraseña incorrectos
- **Solución**: Verificar credenciales o recuperar contraseña

#### E002: Sala No Disponible
- **Causa**: Otra reserva en el mismo horario
- **Solución**: Seleccionar otro horario o sala

#### E003: Permisos Insuficientes
- **Causa**: Intentar acceder a función sin permisos
- **Solución**: Contactar administrador para cambio de rol

#### E004: Datos Inválidos
- **Causa**: Información en formato incorrecto
- **Solución**: Revisar formato de fecha, números, etc.

#### E005: Sesión Expirada
- **Causa**: Tiempo de inactividad excedido
- **Solución**: Iniciar sesión nuevamente

---

## Consejos de Uso

### 💡 Mejores Prácticas

#### Para Reservas Efectivas
1. **Planifica con anticipación**: Reserva con varios días de antelación
2. **Revisa equipamiento**: Verifica que la sala tiene lo que necesitas
3. **Confirma asistencia**: Ajusta el número de asistentes realísticamente
4. **Lee políticas**: Entiende las reglas de cancelación
5. **Llega puntual**: Respeta los horarios de otros usuarios

#### Para Mejor Experiencia
1. **Favoritos**: Guarda salas que uses frecuentemente
2. **Filtros**: Usa filtros para encontrar salas más rápido
3. **Notificaciones**: Configura recordatorios de reservas
4. **Califica**: Ayuda a mejorar el sistema calificando salas
5. **Actualiza**: Mantén tu información de perfil actualizada

### 🏆 Recomendaciones por Tipo de Usuario

#### Para Estudiantes
- Reserva salas de estudio para grupos pequeños
- Aprovecha las salas gratuitas disponibles
- Califica las salas para ayudar a otros estudiantes
- Planifica sesiones de estudio con anticipación

#### Para Profesores
- Reserva laboratorios para clases prácticas
- Usa auditorios para conferencias y presentaciones
- Considera la capacidad al planificar eventos
- Coordina con otros profesores para evitar conflictos

#### Para Administradores
- Monitorea estadísticas regularmente
- Gestiona conflictos de reservas proactivamente
- Mantén información de salas actualizada
- Responde rápidamente a reportes de problemas

---

*¿Necesitas más ayuda? Consulta la documentación técnica o contacta al equipo de soporte.*

**Última actualización**: Junio 2025
**Versión del manual**: 1.0
