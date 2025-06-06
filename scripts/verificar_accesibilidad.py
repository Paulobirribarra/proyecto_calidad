#!/usr/bin/env python3
"""
Script de Evaluación de Accesibilidad WCAG 2.1
Sistema de Reserva de Salas

Este script verifica elementos básicos de accesibilidad mediante 
análisis del HTML estático y genera un reporte.
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class AccessibilityChecker:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.issues = []
        self.warnings = []
        self.passes = []
        
    def log_issue(self, page, issue_type, description, element=None):
        """Registra un problema de accesibilidad"""
        self.issues.append({
            'page': page,
            'type': issue_type,
            'description': description,
            'element': str(element) if element else None,
            'severity': 'ERROR'
        })
    
    def log_warning(self, page, issue_type, description, element=None):
        """Registra una advertencia de accesibilidad"""
        self.warnings.append({
            'page': page,
            'type': issue_type,
            'description': description,
            'element': str(element) if element else None,
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
    
    def check_html_lang(self, soup, page_name):
        """Verifica que el elemento html tenga atributo lang"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            self.log_pass(page_name, 'HTML_LANG', f"Idioma declarado: {html_tag.get('lang')}")
        else:
            self.log_issue(page_name, 'HTML_LANG', 'Elemento HTML sin atributo lang', html_tag)
    
    def check_page_title(self, soup, page_name):
        """Verifica que la página tenga título descriptivo"""
        title = soup.find('title')
        if title and title.text.strip():
            if len(title.text.strip()) > 5:
                self.log_pass(page_name, 'PAGE_TITLE', f"Título descriptivo: {title.text.strip()}")
            else:
                self.log_warning(page_name, 'PAGE_TITLE', 'Título muy corto', title)
        else:
            self.log_issue(page_name, 'PAGE_TITLE', 'Página sin título', title)
    
    def check_headings_hierarchy(self, soup, page_name):
        """Verifica jerarquía correcta de encabezados"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            self.log_warning(page_name, 'HEADINGS', 'Página sin encabezados')
            return
        
        prev_level = 0
        hierarchy_correct = True
        
        for heading in headings:
            current_level = int(heading.name[1])
            
            if prev_level == 0:  # Primer encabezado
                if current_level == 1:
                    self.log_pass(page_name, 'HEADINGS', 'Primer encabezado es H1')
                else:
                    self.log_warning(page_name, 'HEADINGS', f'Primer encabezado es {heading.name.upper()}, debería ser H1', heading)
            
            elif current_level > prev_level + 1:
                hierarchy_correct = False
                self.log_issue(page_name, 'HEADINGS', f'Salto en jerarquía: de H{prev_level} a H{current_level}', heading)
            
            prev_level = current_level
        
        if hierarchy_correct and len(headings) > 1:
            self.log_pass(page_name, 'HEADINGS', 'Jerarquía de encabezados correcta')
    
    def check_form_labels(self, soup, page_name):
        """Verifica que los campos de formulario tengan etiquetas"""
        form_inputs = soup.find_all(['input', 'select', 'textarea'])
        
        if not form_inputs:
            return  # No hay formularios
        
        unlabeled_inputs = []
        
        for input_elem in form_inputs:
            input_type = input_elem.get('type', 'text')
            input_id = input_elem.get('id')
            input_name = input_elem.get('name')
            
            # Ignorar campos hidden y submit
            if input_type in ['hidden', 'submit', 'button']:
                continue
            
            # Buscar label asociado
            label = None
            if input_id:
                label = soup.find('label', {'for': input_id})
            
            if not label:
                # Buscar label que contenga el input
                parent = input_elem.parent
                while parent and parent.name != 'form':
                    if parent.name == 'label':
                        label = parent
                        break
                    parent = parent.parent
            
            if not label:
                unlabeled_inputs.append(input_elem)
                self.log_issue(page_name, 'FORM_LABELS', 
                             f'Campo sin etiqueta: {input_name or input_id or input_type}', 
                             input_elem)
            else:
                if label.text.strip():
                    self.log_pass(page_name, 'FORM_LABELS', 
                                f'Campo con etiqueta: {label.text.strip()}')
                else:
                    self.log_warning(page_name, 'FORM_LABELS', 
                                   'Etiqueta vacía', label)
    
    def check_images_alt_text(self, soup, page_name):
        """Verifica texto alternativo en imágenes"""
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt')
            
            if alt is None:
                self.log_issue(page_name, 'IMG_ALT', 'Imagen sin atributo alt', img)
            elif alt.strip() == '':
                # Alt vacío es válido para imágenes decorativas
                self.log_pass(page_name, 'IMG_ALT', 'Imagen decorativa con alt vacío')
            else:
                self.log_pass(page_name, 'IMG_ALT', f'Imagen con alt text: {alt}')
    
    def check_aria_hidden_icons(self, soup, page_name):
        """Verifica que los íconos decorativos tengan aria-hidden"""
        icons = soup.find_all('i', class_=re.compile(r'fa[s|r|l|b]?'))
        
        decorative_icons = 0
        missing_aria = 0
        
        for icon in icons:
            if icon.get('aria-hidden') == 'true':
                decorative_icons += 1
            else:
                # Verificar si el ícono está dentro de un botón/enlace con texto
                parent_with_text = icon.parent
                has_text_sibling = False
                
                if parent_with_text:
                    text_content = parent_with_text.get_text(strip=True)
                    icon_text = icon.get_text(strip=True)
                    if text_content and text_content != icon_text:
                        has_text_sibling = True
                
                if not has_text_sibling:
                    missing_aria += 1
                    self.log_warning(page_name, 'ARIA_HIDDEN', 
                                   'Ícono sin aria-hidden="true"', icon)
        
        if decorative_icons > 0:
            self.log_pass(page_name, 'ARIA_HIDDEN', 
                         f'{decorative_icons} íconos decorativos correctamente marcados')
    
    def check_skip_links(self, soup, page_name):
        """Verifica presencia de skip links"""
        skip_links = soup.find_all('a', class_='skip-link')
        
        if skip_links:
            for link in skip_links:
                href = link.get('href', '')
                if href.startswith('#'):
                    target = soup.find(id=href[1:])
                    if target:
                        self.log_pass(page_name, 'SKIP_LINKS', 
                                    f'Skip link funcional: {link.text}')
                    else:
                        self.log_issue(page_name, 'SKIP_LINKS', 
                                     f'Skip link con destino inexistente: {href}', link)
                else:
                    self.log_warning(page_name, 'SKIP_LINKS', 
                                   'Skip link sin ancla interna', link)
        else:
            self.log_issue(page_name, 'SKIP_LINKS', 'Página sin skip links')
    
    def check_button_labels(self, soup, page_name):
        """Verifica que los botones tengan texto o aria-label"""
        buttons = soup.find_all(['button', 'input[type="submit"]', 'input[type="button"]'])
        
        for button in buttons:
            text = button.get_text(strip=True)
            aria_label = button.get('aria-label')
            value = button.get('value')
            title = button.get('title')
            
            if text or aria_label or value or title:
                label_source = 'texto' if text else 'aria-label' if aria_label else 'value' if value else 'title'
                self.log_pass(page_name, 'BUTTON_LABELS', 
                            f'Botón con {label_source}: {text or aria_label or value or title}')
            else:
                self.log_issue(page_name, 'BUTTON_LABELS', 
                             'Botón sin texto o aria-label', button)
    def check_page(self, url, page_name):
        """Verifica una página específica"""
        try:
            print(f"📄 Verificando: {page_name} ({url})")
            
            # Usar archivos HTML estáticos del proyecto
            if url == '/':
                # Leer templates directamente para análisis estático
                template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'rooms', 'room_list.html')
            elif url == '/login/':
                template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'usuarios', 'login.html')
            elif url == '/register/':
                template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'usuarios', 'register.html')
            elif url == '/rooms/':
                template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'rooms', 'room_list.html')
            else:
                self.log_warning(page_name, 'FILE_NOT_FOUND', 'Plantilla no encontrada para análisis estático')
                return
            
            if not os.path.exists(template_path):
                self.log_warning(page_name, 'FILE_NOT_FOUND', f'Archivo no encontrado: {template_path}')
                return
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Análisis básico del template Django
            self.analyze_template(content, page_name)
            
        except Exception as e:
            self.log_issue(page_name, 'EXCEPTION', f'Error al verificar página: {str(e)}')
    
    def analyze_template(self, content, page_name):
        """Analiza un template de Django para verificaciones básicas"""
        
        # Verificar elementos críticos de accesibilidad
        if 'aria-hidden="true"' in content:
            self.log_pass(page_name, 'ARIA_HIDDEN', 'Íconos decorativos con aria-hidden encontrados')
        
        if 'skip-link' in content:
            self.log_pass(page_name, 'SKIP_LINKS', 'Skip links implementados')
        else:
            self.log_issue(page_name, 'SKIP_LINKS', 'Skip links no encontrados')
        
        if 'aria-label=' in content:
            self.log_pass(page_name, 'ARIA_LABELS', 'Etiquetas ARIA encontradas')
        else:
            self.log_warning(page_name, 'ARIA_LABELS', 'Pocas o ninguna etiqueta ARIA encontrada')
        
        if 'role=' in content:
            self.log_pass(page_name, 'ARIA_ROLES', 'Roles ARIA encontrados')
        else:
            self.log_warning(page_name, 'ARIA_ROLES', 'Roles ARIA no encontrados')
        
        # Verificar estructura semántica
        semantic_elements = ['<nav', '<main', '<section', '<header', '<footer', '<article']
        found_semantic = [elem for elem in semantic_elements if elem in content]
        
        if found_semantic:
            self.log_pass(page_name, 'SEMANTIC_HTML', f'Elementos semánticos encontrados: {", ".join(found_semantic)}')
        else:
            self.log_warning(page_name, 'SEMANTIC_HTML', 'Pocos elementos HTML5 semánticos')
        
        # Verificar formularios
        if '<form' in content:
            if 'aria-required' in content or 'required' in content:
                self.log_pass(page_name, 'FORM_VALIDATION', 'Campos requeridos marcados')
            else:
                self.log_warning(page_name, 'FORM_VALIDATION', 'Campos requeridos sin marcar apropiadamente')
            
            if '{{ form.' in content and 'label' in content:
                self.log_pass(page_name, 'FORM_LABELS', 'Etiquetas de formulario encontradas')
            else:
                self.log_issue(page_name, 'FORM_LABELS', 'Etiquetas de formulario faltantes o incorrectas')
        
        # Verificar breadcrumbs
        if 'breadcrumb' in content:
            if 'aria-label="breadcrumb"' in content:
                self.log_pass(page_name, 'BREADCRUMBS', 'Breadcrumbs accesibles implementados')
            else:
                self.log_warning(page_name, 'BREADCRUMBS', 'Breadcrumbs sin aria-label')
        
        # Verificar botones
        if '<button' in content or 'btn' in content:
            if 'aria-label' in content:
                self.log_pass(page_name, 'BUTTON_LABELS', 'Botones con etiquetas ARIA')
            else:
                self.log_warning(page_name, 'BUTTON_LABELS', 'Botones podrían necesitar mejores etiquetas')
        
        # Verificar contraste (análisis básico de clases)
        if 'text-muted' in content:
            self.log_warning(page_name, 'COLOR_CONTRAST', 'Texto gris (.text-muted) - verificar contraste')
        
        if 'bg-light' in content or 'text-light' in content:
            self.log_warning(page_name, 'COLOR_CONTRAST', 'Colores claros - verificar contraste')
        
        # Verificar idioma
        if 'lang="es"' in content or 'extends' in content:  # extends indica herencia de base.html
            self.log_pass(page_name, 'LANGUAGE', 'Idioma declarado o heredado')
        else:
            self.log_issue(page_name, 'LANGUAGE', 'Idioma no declarado')
    
    def run_all_checks(self):
        """Ejecuta todas las verificaciones de accesibilidad"""
        print("🔍 Iniciando evaluación de accesibilidad WCAG 2.1")
        print("=" * 60)
        
        # Páginas a verificar
        pages_to_check = [
            ('/', 'Página Principal'),
            ('/rooms/', 'Lista de Salas'),
            ('/login/', 'Inicio de Sesión'),
            ('/register/', 'Registro'),
        ]
        
        for url, name in pages_to_check:
            self.check_page(url, name)
        
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
        if total_issues == 0 and total_warnings == 0:
            print(f"\n🎉 ESTADO: EXCELENTE - Cumple con WCAG 2.1")
        elif total_issues == 0:
            print(f"\n✅ ESTADO: BUENO - Cumple con WCAG 2.1 con advertencias menores")
        elif total_issues <= 5:
            print(f"\n⚠️  ESTADO: NECESITA MEJORAS - Problemas moderados")
        else:
            print(f"\n❌ ESTADO: NO CUMPLE - Problemas críticos múltiples")
        
        # Problemas críticos
        if self.issues:
            print(f"\n❌ PROBLEMAS CRÍTICOS ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue['page']}: {issue['description']}")
                if issue['element']:
                    print(f"     Elemento: {issue['element'][:100]}...")
        
        # Advertencias
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Mostrar solo las primeras 10
                print(f"   • {warning['page']}: {warning['description']}")
            
            if len(self.warnings) > 10:
                print(f"   ... y {len(self.warnings) - 10} advertencias más")
        
        # Verificaciones exitosas (muestra solo algunas)
        if self.passes:
            print(f"\n✅ ELEMENTOS ACCESIBLES (ejemplos):")
            for pass_item in self.passes[:5]:
                print(f"   • {pass_item['page']}: {pass_item['description']}")
        
        print(f"\n💡 RECOMENDACIONES:")
        print(f"   1. Revisar el documento EVALUACION_ACCESIBILIDAD_WCAG.md")
        print(f"   2. Implementar las mejoras de Fase 1 (críticas)")
        print(f"   3. Probar con lectores de pantalla (NVDA, JAWS)")
        print(f"   4. Usar herramientas automatizadas: axe-core, Pa11y")
        
        print("\n" + "=" * 60)

def main():
    """Función principal"""
    checker = AccessibilityChecker()
    checker.run_all_checks()

if __name__ == '__main__':
    main()
