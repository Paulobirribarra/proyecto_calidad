"""
URL configuration for proyecto_calidad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse
from django.views.decorators.http import require_GET
import os

# Configurar manejadores de errores personalizados
handler404 = 'usuarios.views.custom_404'
handler500 = 'usuarios.views.custom_500' 
handler403 = 'usuarios.views.custom_403'

@require_GET
def robots_txt(request):
    """Servir robots.txt para seguridad y SEO"""
    robots_path = os.path.join(settings.BASE_DIR, 'robots.txt')
    try:
        with open(robots_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        # Robots.txt básico si no existe el archivo
        basic_robots = """User-agent: *
Disallow: /admin/
Disallow: /api/
Allow: /
"""
        return HttpResponse(basic_robots, content_type='text/plain')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # SEO y Seguridad
    path('robots.txt', robots_txt, name='robots_txt'),
    
    # Aplicaciones
    path('usuarios/', include('usuarios.urls')),
    path('salas/', include('rooms.urls')),
    
    # Redirigir la raíz a la lista de salas
    path('', RedirectView.as_view(url='/salas/', permanent=False), name='home'),
]

# Configuración para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'MEDIA_URL'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
