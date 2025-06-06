from django.shortcuts import render

# Create your views here.

def error_403(request, exception=None):
    """Vista personalizada para manejar el error 403 (Acceso Prohibido)"""
    error_message = 'No tienes permisos para acceder a esta página o realizar esta acción.'
    
    # Si hay una excepción específica con mensaje, usarla
    if exception and hasattr(exception, 'args') and len(exception.args) > 0:
        error_message = exception.args[0]
    
    context = {
        'error_code': 403,
        'error_message': error_message,
        'exception': exception
    }
    return render(request, 'errors/403.html', context, status=403)
