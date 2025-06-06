# Template tags package

from django import template
from django.forms.widgets import Widget

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Agrega clases CSS a un campo de formulario.
    
    Uso: {{ form.field|add_class:"form-control" }}
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field

@register.filter(name='add_aria')
def add_aria(field, aria_attrs):
    """
    Agrega atributos ARIA a un campo de formulario.
    
    Uso: {{ form.field|add_aria:"required:true,describedby:help-text" }}
    """
    if not hasattr(field, 'as_widget'):
        return field
    
    attrs = {}
    for attr in aria_attrs.split(','):
        if ':' in attr:
            key, value = attr.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'required':
                attrs['aria-required'] = value
            elif key == 'describedby':
                attrs['aria-describedby'] = value
            elif key == 'label':
                attrs['aria-label'] = value
            elif key == 'invalid':
                attrs['aria-invalid'] = value
    
    return field.as_widget(attrs=attrs)

@register.filter(name='add_accessibility')
def add_accessibility(field, config=""):
    """
    Agrega múltiples atributos de accesibilidad de una vez.
    
    Uso: {{ form.field|add_accessibility:"form-control,required,help:field-help" }}
    """
    if not hasattr(field, 'as_widget'):
        return field
    
    attrs = {}
    css_classes = []
    
    if config:
        parts = config.split(',')
        for part in parts:
            part = part.strip()
            
            if ':' in part:
                key, value = part.split(':', 1)
                if key == 'help':
                    attrs['aria-describedby'] = value
                elif key == 'label':
                    attrs['aria-label'] = value
            elif part == 'required':
                attrs['aria-required'] = 'true'
            elif part in ['form-control', 'form-select', 'form-check-input']:
                css_classes.append(part)
    
    if css_classes:
        attrs['class'] = ' '.join(css_classes)
    
    return field.as_widget(attrs=attrs)
