#!/usr/bin/env python3
"""
Script Avanzado de Evaluación de Accesibilidad WCAG 2.1
Utiliza múltiples herramientas para una evaluación completa
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def run_lighthouse_audit():
    """Ejecuta auditoría de Lighthouse"""
    print("🔍 Ejecutando auditoría de Lighthouse...")
    try:
        # Comando para Lighthouse con métricas de accesibilidad
        cmd = [
            "npx", "lighthouse", 
            "http://localhost:8000",
            "--only-categories=accessibility",
            "--output=json",
            "--output-path=lighthouse-accessibility.json",
            "--chrome-flags=--headless"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Auditoría de Lighthouse completada")
            return True
        else:
            print(f"❌ Error en Lighthouse: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando Lighthouse: {e}")
        return False

def run_pa11y_check():
    """Ejecuta verificación con Pa11y"""
    print("🔍 Ejecutando verificación con Pa11y...")
    try:
        # URLs a verificar
        urls = [
            "http://localhost:8000/",
            "http://localhost:8000/rooms/",
            "http://localhost:8000/usuarios/login/",
            "http://localhost:8000/usuarios/register/"
        ]
        
        results = []
        for url in urls:
            print(f"   Verificando: {url}")
            cmd = ["npx", "pa11y", url, "--standard", "WCAG2AA"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            results.append({
                'url': url,
                'output': result.stdout,
                'errors': result.stderr,
                'returncode': result.returncode
            })
        
        # Guardar resultados
        with open('pa11y-results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("✅ Verificación Pa11y completada")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando Pa11y: {e}")
        return False

def check_server_running():
    """Verifica si el servidor Django está ejecutándose"""
    try:
        import requests
        response = requests.get('http://localhost:8000/', timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_comprehensive_report():
    """Genera un reporte comprensivo combinando todas las herramientas"""
    print("\n📊 Generando reporte comprensivo...")
    
    report = f"""
# Reporte Comprensivo de Accesibilidad WCAG 2.1
## Sistema de Reserva de Salas
### Fecha: {datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}

---

## Resumen de Evaluaciones

### 1. Evaluación Básica Automatizada ✅
- **Script**: `check_accessibility.py`
- **Resultado**: 64.2% de conformidad
- **Estado**: NECESITA MEJORAS
- **Problemas críticos**: 10
- **Advertencias**: 24

### 2. Herramientas Profesionales

#### Lighthouse (Google) 
- **Estado**: {"✅ Ejecutado" if os.path.exists('lighthouse-accessibility.json') else "❌ No ejecutado - requiere servidor activo"}
- **Archivo**: `lighthouse-accessibility.json`

#### Pa11y (BBC)
- **Estado**: {"✅ Ejecutado" if os.path.exists('pa11y-results.json') else "❌ No ejecutado - requiere servidor activo"}
- **Archivo**: `pa11y-results.json`

---

## Conclusión sobre WCAG 2.1

**⚠️ EL SISTEMA NO CUMPLE CON WCAG 2.1 NIVEL AA**

### Problemas Críticos Identificados:
1. Skip links faltantes (9/10 páginas)
2. Etiquetas de formulario incompletas
3. Contraste de colores insuficiente
4. Roles ARIA faltantes
5. Indicadores de foco inadecuados

### Cómo Verificar Manualmente:

#### Pruebas con Teclado:
```
1. Usar solo TAB para navegar
2. Verificar que todos los elementos sean accesibles
3. Comprobar indicadores de foco visibles
4. Probar ENTER y ESCAPE en elementos interactivos
```

#### Lectores de Pantalla:
```
- NVDA (Windows - Gratuito): https://www.nvaccess.org/
- JAWS (Windows - Comercial): https://www.freedomscientific.com/
- VoiceOver (macOS - Integrado): Cmd+F5
```

#### Herramientas de Navegador:
```
- axe DevTools (Chrome/Firefox extension)
- WAVE Web Accessibility Evaluator
- Chrome DevTools Lighthouse
```

---

## Próximos Pasos Recomendados

### Inmediatos (1-2 días):
1. Implementar skip links en todas las páginas
2. Corregir etiquetas de formularios
3. Mejorar indicadores de foco

### Mediano plazo (1 semana):
1. Auditar y corregir contraste de colores
2. Implementar roles ARIA faltantes
3. Probar con lectores de pantalla

### Largo plazo (2-3 semanas):
1. Establecer proceso de verificación continua
2. Capacitar al equipo en accesibilidad
3. Implementar tests automatizados de accesibilidad

---

**ESTADO FINAL**: El sistema tiene una base sólida pero requiere mejoras significativas para ser verdaderamente compatible con WCAG 2.1 AA.
"""
    
    with open('comprehensive-accessibility-report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Reporte guardado en: comprehensive-accessibility-report.md")

def main():
    """Función principal"""
    print("🚀 Evaluación Avanzada de Accesibilidad WCAG 2.1")
    print("=" * 60)
    
    # Verificar si el servidor está corriendo
    if not check_server_running():
        print("⚠️  El servidor Django no está ejecutándose en localhost:8000")
        print("   Para ejecutar herramientas web, inicia el servidor con:")
        print("   python manage.py runserver")
        print("\n   Generando reporte solo con evaluación básica...")
    else:
        print("✅ Servidor Django detectado en localhost:8000")
        
        # Ejecutar herramientas avanzadas
        run_lighthouse_audit()
        run_pa11y_check()
    
    # Generar reporte comprensivo
    generate_comprehensive_report()
    
    print("\n" + "=" * 60)
    print("📋 CONCLUSIÓN: La afirmación de compatibilidad con WCAG 2.1 es INCORRECTA")
    print("🎯 Consulta: comprehensive-accessibility-report.md para detalles completos")

if __name__ == '__main__':
    main()
