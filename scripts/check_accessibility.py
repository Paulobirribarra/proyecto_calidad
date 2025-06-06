#!/usr/bin/env python3
"""
Script Simplificado de Evaluación de Accesibilidad WCAG 2.1
Sistema de Reserva de Salas

Este script analiza los templates de Django para verificar
elementos básicos de accesibilidad.
"""

import os
import sys

class AccessibilityChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passes = []
        
    def log_issue(self, page, issue_type, description):
        """Registra un problema de accesibilidad"""
        self.issues.append({
            'page': page,
            'type': issue_type,
            'description': description,
            'severity': 'ERROR'
        })
    
    def log_warning(self, page, issue_type, description):
        """Registra una advertencia de accesibilidad"""
        self.warnings.append({
            'page': page,
            'type': issue_type,
            'description': description,
            'severity': 'WARNING'
        })
    
    def log_pass(self, page, check_type, description):
        """Registra una verificación exitosa"""
        self.passes.append({
            'page': page,
            'type': check_type,
            'description': description,
            'severity': 'PASS'
        })
    
    def analyze_template(self, content, page_name):
        """Analiza un template de Django para verificaciones básicas"""
        
        # Verificar elementos críticos de accesibilidad
        if 'aria-hidden="true"' in content:
            count = content.count('aria-hidden="true"')
            self.log_pass(page_name, 'ARIA_HIDDEN', f'{count} íconos decorativos con aria-hidden')
        else:
            self.log_warning(page_name, 'ARIA_HIDDEN', 'No se encontraron íconos con aria-hidden')
        
        if 'skip-link' in content:
            self.log_pass(page_name, 'SKIP_LINKS', 'Skip links implementados')
        else:
            self.log_issue(page_name, 'SKIP_LINKS', 'Skip links no encontrados')
        
        if 'aria-label=' in content:
            count = content.count('aria-label=')
            self.log_pass(page_name, 'ARIA_LABELS', f'{count} etiquetas ARIA encontradas')
        else:
            self.log_warning(page_name, 'ARIA_LABELS', 'Pocas etiquetas ARIA encontradas')
        
        if 'role=' in content:
            count = content.count('role=')
            self.log_pass(page_name, 'ARIA_ROLES', f'{count} roles ARIA encontrados')
        else:
            self.log_warning(page_name, 'ARIA_ROLES', 'Roles ARIA no encontrados')
        
        # Verificar estructura semántica
        semantic_elements = ['<nav', '<main', '<section', '<header', '<footer', '<article']
        found_semantic = [elem for elem in semantic_elements if elem in content]
        
        if found_semantic:
            self.log_pass(page_name, 'SEMANTIC_HTML', f'Elementos semánticos: {", ".join(found_semantic)}')
        else:
            self.log_warning(page_name, 'SEMANTIC_HTML', 'Pocos elementos HTML5 semánticos')
        
        # Verificar formularios
        if '<form' in content:
            if 'aria-required' in content or 'required' in content:
                self.log_pass(page_name, 'FORM_VALIDATION', 'Campos requeridos marcados')
            else:
                self.log_warning(page_name, 'FORM_VALIDATION', 'Campos requeridos sin marcar')
            
            if 'form-label' in content or 'label for=' in content:
                self.log_pass(page_name, 'FORM_LABELS', 'Etiquetas de formulario encontradas')
            else:
                self.log_issue(page_name, 'FORM_LABELS', 'Etiquetas de formulario faltantes')
        
        # Verificar breadcrumbs
        if 'breadcrumb' in content:
            if 'aria-label="breadcrumb"' in content:
                self.log_pass(page_name, 'BREADCRUMBS', 'Breadcrumbs accesibles')
            else:
                self.log_warning(page_name, 'BREADCRUMBS', 'Breadcrumbs sin aria-label')
        
        # Verificar botones
        if '<button' in content:
            if 'aria-label' in content:
                self.log_pass(page_name, 'BUTTON_LABELS', 'Botones con etiquetas ARIA')
            else:
                self.log_warning(page_name, 'BUTTON_LABELS', 'Algunos botones podrían necesitar aria-label')
        
        # Verificar contraste
        contrast_issues = 0
        if 'text-muted' in content:
            contrast_issues += content.count('text-muted')
        if contrast_issues > 0:
            self.log_warning(page_name, 'COLOR_CONTRAST', f'{contrast_issues} elementos con texto gris - verificar contraste')
        
        # Verificar idioma
        if 'lang="es"' in content or 'extends' in content:
            self.log_pass(page_name, 'LANGUAGE', 'Idioma declarado o heredado')
        else:
            self.log_issue(page_name, 'LANGUAGE', 'Idioma no declarado')
        
        # Verificar navegación
        if 'navbar' in content and 'role="navigation"' in content:
            self.log_pass(page_name, 'NAVIGATION', 'Navegación con role correcto')
        elif 'navbar' in content:
            self.log_warning(page_name, 'NAVIGATION', 'Navegación sin role="navigation"')
        
        # Verificar imágenes
        if '<img' in content:
            if 'alt=' in content:
                self.log_pass(page_name, 'IMG_ALT', 'Imágenes con atributo alt')
            else:
                self.log_issue(page_name, 'IMG_ALT', 'Imágenes sin atributo alt')
        
        # Verificar modales
        if 'modal' in content:
            if 'aria-labelledby' in content or 'aria-describedby' in content:
                self.log_pass(page_name, 'MODALS', 'Modales con etiquetas ARIA')
            else:
                self.log_warning(page_name, 'MODALS', 'Modales sin aria-labelledby/describedby')
    
    def check_template_file(self, file_path, page_name):
        """Verifica un archivo de template específico"""
        try:
            print(f"📄 Analizando: {page_name} ({file_path})")
            
            if not os.path.exists(file_path):
                self.log_warning(page_name, 'FILE_NOT_FOUND', f'Archivo no encontrado: {file_path}')
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.analyze_template(content, page_name)
            
        except Exception as e:
            self.log_issue(page_name, 'EXCEPTION', f'Error al analizar: {str(e)}')
    
    def run_all_checks(self):
        """Ejecuta todas las verificaciones de accesibilidad"""
        print("🔍 Iniciando evaluación de accesibilidad WCAG 2.1")
        print("📊 Análisis estático de templates Django")
        print("=" * 60)
        
        # Directorio base de templates
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        
        # Templates a verificar
        templates_to_check = [
            ('base.html', 'Template Base'),
            ('rooms/room_list.html', 'Lista de Salas'),
            ('rooms/room_detail.html', 'Detalle de Sala'),
            ('rooms/room_reserve.html', 'Reservar Sala'),
            ('rooms/reservation_list.html', 'Mis Reservas'),
            ('rooms/room_review.html', 'Calificar Sala'),
            ('usuarios/login.html', 'Inicio de Sesión'),
            ('usuarios/register.html', 'Registro'),
            ('usuarios/profile.html', 'Perfil de Usuario'),
            ('errors/404.html', 'Página de Error 404'),
        ]
        
        for template_path, name in templates_to_check:
            full_path = os.path.join(templates_dir, template_path)
            self.check_template_file(full_path, name)
        
        self.print_report()
    
    def print_report(self):
        """Imprime el reporte de accesibilidad"""
        print("\n" + "=" * 60)
        print("📊 REPORTE DE ACCESIBILIDAD WCAG 2.1")
        print("=" * 60)
        
        # Resumen
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        total_passes = len(self.passes)
        
        print(f"\n📈 RESUMEN:")
        print(f"   ✅ Verificaciones exitosas: {total_passes}")
        print(f"   ⚠️  Advertencias: {total_warnings}")
        print(f"   ❌ Problemas críticos: {total_issues}")
        
        # Estado general
        conformity_score = (total_passes / (total_passes + total_warnings + total_issues)) * 100 if (total_passes + total_warnings + total_issues) > 0 else 0
        
        print(f"\n📊 PUNTUACIÓN DE CONFORMIDAD: {conformity_score:.1f}%")
        
        if conformity_score >= 90:
            print("🎉 ESTADO: EXCELENTE - Alta conformidad con WCAG 2.1")
        elif conformity_score >= 70:
            print("✅ ESTADO: BUENO - Conformidad moderada, mejoras menores necesarias")
        elif conformity_score >= 50:
            print("⚠️  ESTADO: NECESITA MEJORAS - Problemas moderados")
        else:
            print("❌ ESTADO: NO CUMPLE - Problemas críticos múltiples")
        
        # Análisis por categorías
        categories = {}
        for item in self.issues + self.warnings + self.passes:
            cat = item['type']
            if cat not in categories:
                categories[cat] = {'pass': 0, 'warning': 0, 'error': 0}
            
            if item['severity'] == 'PASS':
                categories[cat]['pass'] += 1
            elif item['severity'] == 'WARNING':
                categories[cat]['warning'] += 1
            else:
                categories[cat]['error'] += 1
        
        print(f"\n📋 ANÁLISIS POR CATEGORÍAS:")
        for cat, counts in sorted(categories.items()):
            total_cat = sum(counts.values())
            success_rate = (counts['pass'] / total_cat) * 100 if total_cat > 0 else 0
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            print(f"   {status} {cat}: {success_rate:.0f}% ({counts['pass']}✅ {counts['warning']}⚠️ {counts['error']}❌)")
        
        # Problemas críticos
        if self.issues:
            print(f"\n❌ PROBLEMAS CRÍTICOS QUE REQUIEREN ATENCIÓN INMEDIATA:")
            for issue in self.issues[:10]:  # Mostrar solo los primeros 10
                print(f"   • {issue['page']}: {issue['description']}")
            
            if len(self.issues) > 10:
                print(f"   ... y {len(self.issues) - 10} problemas más")
        
        # Advertencias importantes
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS PRINCIPALES:")
            warning_counts = {}
            for warning in self.warnings:
                desc = warning['description']
                warning_counts[desc] = warning_counts.get(desc, 0) + 1
            
            for desc, count in sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {desc} ({count} ocurrencias)")
        
        # Fortalezas
        if self.passes:
            print(f"\n✅ FORTALEZAS DEL SISTEMA:")
            pass_counts = {}
            for pass_item in self.passes:
                desc = pass_item['description']
                pass_counts[desc] = pass_counts.get(desc, 0) + 1
            
            for desc, count in sorted(pass_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {desc} ({count} implementaciones)")
        
        print(f"\n💡 RECOMENDACIONES PRIORITARIAS:")
        print(f"   1. 🚨 Revisar y corregir problemas críticos listados arriba")
        print(f"   2. 📖 Consultar EVALUACION_ACCESIBILIDAD_WCAG.md para detalles")
        print(f"   3. 🛠️  Implementar mejoras de Fase 1 (etiquetas, roles ARIA)")
        print(f"   4. 🎨 Verificar contraste de colores con herramientas especializadas")
        print(f"   5. 🔊 Probar con lectores de pantalla (NVDA, JAWS, VoiceOver)")
        print(f"   6. 🤖 Usar herramientas automatizadas: axe-core, Pa11y, Lighthouse")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        if total_issues > 0:
            print(f"   • Prioridad ALTA: Corregir {total_issues} problemas críticos")
        if total_warnings > 5:
            print(f"   • Prioridad MEDIA: Revisar {total_warnings} advertencias")
        print(f"   • Implementar plan de mejoras por fases")
        print(f"   • Establecer proceso de validación continua")
        
        print("\n" + "=" * 60)
        print("📋 NOTA: Esta es una evaluación básica automatizada.")
        print("🔍 Se recomienda complementar con:")
        print("   - Pruebas manuales con teclado")
        print("   - Evaluación con lectores de pantalla")
        print("   - Herramientas especializadas de accesibilidad")
        print("   - Revisión por expertos en UX accesible")

def main():
    """Función principal"""
    print("🚀 Sistema de Evaluación de Accesibilidad WCAG 2.1")
    print("🏢 Sistema de Reserva de Salas")
    print()
    
    checker = AccessibilityChecker()
    checker.run_all_checks()

if __name__ == '__main__':
    main()
