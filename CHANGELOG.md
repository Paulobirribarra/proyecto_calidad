# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-04

### ✅ Agregado
- Sistema completo de gestión de salas de estudio
- Autenticación y gestión de usuarios
- Sistema de reservas con validación de disponibilidad
- Panel de administración completo
- Skip links para navegación accesible en todos los templates críticos
- Estructura semántica HTML5 con elementos `<main>` y roles ARIA
- Documentación técnica completa
- Manual de usuario interactivo
- Scripts de configuración automatizada
- Pruebas de accesibilidad automatizadas

### ♿ Accesibilidad WCAG 2.1
- **Conformidad:** 87.5% Nivel AA
- **Problemas críticos resueltos:** 4/4 (100%)
- Skip links implementados en:
  - `room_list.html` - Navegación de lista de salas
  - `room_detail.html` - Detalles y panel de reserva
  - `room_reserve.html` - Formulario de reserva
  - `login.html` - Formulario de autenticación
  - `profile.html` - Información de perfil
  - `reservation_list.html` - Lista de reservas

### 🔧 Mejoras Técnicas
- Estructura Bootstrap corregida en todos los templates
- Optimización de ancho de contenido (container vs container-fluid)
- IDs específicos para navegación por secciones
- Elementos semánticos mejorados
- Roles ARIA implementados
- Navegación por teclado optimizada

### 📚 Documentación
- Documentación reorganizada en carpeta `documentacion/`
- Índice completo de documentación (INDEX.md)
- Informes de accesibilidad actualizados
- Documentación de seguridad
- Manual de usuario
- Documentación técnica

### 🔒 Seguridad
- Protección CSRF implementada
- Validación de entradas
- Sanitización de datos
- Protección contra inyección SQL
- Autenticación segura

### 🛠️ Infraestructura
- Requirements.txt actualizado con versiones exactas
- .gitignore completo para Django
- README.md principal del proyecto
- Changelog para control de versiones
- Scripts de pruebas automatizadas

## [0.2.0] - 2025-06-03

### Agregado
- Implementación inicial de skip links
- Scripts de verificación de accesibilidad
- Documentación de seguridad

### Corregido
- Problemas de estructura HTML
- Validaciones de formularios

## [0.1.0] - 2025-06-02

### Agregado
- Implementación inicial del sistema
- Modelos de salas, usuarios y reservas
- Templates básicos
- Funcionalidad core del sistema

---

**Formato de versiones:**
- **Mayor.Menor.Parche** (Semantic Versioning)
- **Mayor:** Cambios incompatibles
- **Menor:** Funcionalidad nueva compatible
- **Parche:** Correcciones de bugs compatibles
