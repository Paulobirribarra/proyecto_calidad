# Compartir la Aplicación Django con Ngrok

Esta guía te explicará cómo compartir tu aplicación Django temporalmente a través de Internet utilizando Ngrok, lo que permitirá que otras personas puedan acceder a tu aplicación durante la demostración sin necesidad de configuraciones complejas.

## 1. Instalar Ngrok

Si aún no tienes Ngrok instalado:

1. Descarga Ngrok desde [https://ngrok.com/download](https://ngrok.com/download)
2. Extrae el archivo descargado a una ubicación accesible en tu sistema

Alternativamente, puedes instalarlo con pip:

```powershell
pip install pyngrok
```

## 2. Ejecutar tu aplicación Django

Primero, asegúrate de que tu aplicación Django está funcionando en el puerto por defecto (8000):

```powershell
cd e:\Desktop\Final_QA\proyecto_calidad
python manage.py runserver
```

## 3. Configurar ALLOWED_HOSTS en Django

Para que Ngrok funcione correctamente con Django, necesitas configurar ALLOWED_HOSTS para aceptar el dominio de Ngrok:

1. Abre el archivo `settings.py`:

```powershell
# Abre el archivo en tu editor de código
code e:\Desktop\Final_QA\proyecto_calidad\proyecto_calidad\settings.py
```

2. Edita la configuración ALLOWED_HOSTS para incluir todos los dominios durante la demostración:

```python
# Permite cualquier host durante la demostración (NO USAR EN PRODUCCIÓN)
ALLOWED_HOSTS = ['*']
```

Guarda el archivo después de hacer los cambios.

## 4. Iniciar el túnel de Ngrok

### Método 1: Si instalaste Ngrok como aplicación independiente

Abre una nueva terminal y ejecuta:

```powershell
# Cambia la ruta al directorio donde está tu ejecutable ngrok
cd ruta\a\ngrok
.\ngrok.exe http 8000
```

### Método 2: Si instalaste pyngrok con pip

```powershell
cd e:\Desktop\Final_QA\proyecto_calidad
python -m pyngrok.ngrok http 8000
```

## 5. Obtener la URL pública

Después de ejecutar Ngrok, verás algo como esto en la terminal:

```
Session Status                online
Account                       Tu Cuenta (Plan: Free)
Version                       3.x.x
Region                        xxxx
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxx-xxx-xxx-xxx.ngrok-free.app -> http://localhost:8000
```

La URL pública es: `https://xxxx-xxx-xxx-xxx-xxx.ngrok-free.app`

## 6. Compartir la URL

Ahora puedes compartir esta URL con cualquier persona y podrán acceder a tu aplicación, incluso si están fuera de tu red local.

## 7. Demostración de seguridad a través de Ngrok

Una vez configurado Ngrok, puedes realizar la demostración de pruebas de seguridad utilizando la URL proporcionada por Ngrok:

1. Navega a `https://xxxx-xxx-xxx-xxx-xxx.ngrok-free.app/usuarios/login/`
2. Intenta la inyección SQL: `' OR 1=1 --` como nombre de usuario y cualquier contraseña
3. Intenta la inyección SQL destructiva: `'; DROP TABLE users; --`
4. Demuestra que ambos intentos fallan y la aplicación permanece segura

## Consideraciones importantes

1. La URL de Ngrok cambia cada vez que inicias el servicio (a menos que tengas una cuenta de pago)
2. La configuración `ALLOWED_HOSTS = ['*']` es solo para demostraciones, no para entornos de producción
3. Ngrok en su versión gratuita tiene limitaciones de velocidad y conexiones simultáneas
4. No dejes Ngrok ejecutándose indefinidamente, ya que expone tu aplicación a Internet

## Solución de problemas comunes

- Si recibes errores 400 o 502, verifica que tu aplicación Django esté funcionando correctamente
- Si Django muestra errores de "Invalid HTTP_HOST header", asegúrate de que ALLOWED_HOSTS incluya '*' o el dominio específico de Ngrok
- Si el túnel se desconecta frecuentemente, puede ser debido a las limitaciones de la cuenta gratuita de Ngrok
