# Demostración Simple de Seguridad - Inyección SQL

Esta guía te permite mostrar de manera rápida y visual cómo el formulario de login está protegido contra la inyección SQL más común.

## Preparación

1. Asegúrate de tener el servidor Django en ejecución:
   ```
   cd e:\Desktop\Final_QA\proyecto_calidad
   python manage.py runserver
   ```

2. Abre el navegador y navega a la página de login:
   ```
   http://127.0.0.1:8000/usuarios/login/
   ```

## Demostración de Inyección SQL

### Paso 1: Explica el ataque

Explica brevemente que la inyección SQL `' OR 1=1 --` es un ataque clásico que intenta manipular la consulta SQL:

```sql
SELECT * FROM usuarios WHERE username = '' OR 1=1 -- ' AND password = 'cualquiercosa'
```

Esta consulta maliciosa siempre devuelve VERDADERO porque `1=1` siempre es verdadero, y el `--` comenta el resto de la consulta, ignorando la verificación de contraseña.

### Paso 2: Muestra la protección en acción

1. En el formulario de login, introduce:
   - **Usuario**: `' OR 1=1 --`
   - **Contraseña**: `cualquiercosa`

2. Haz clic en "Iniciar sesión"

3. Observa que el sistema rechaza el intento con el mensaje:
   ```
   No existe un usuario con ese nombre.
   ```

### Paso 3: Explica por qué funciona la protección

Django utiliza consultas parametrizadas que separan los datos de la estructura SQL:

```python
# En lugar de construir una consulta como:
"SELECT * FROM usuarios WHERE username = '" + username_input + "' AND password = '" + password_input + "'"

# Django usa consultas parametrizadas:
User.objects.filter(username=username_input).first()
```

En una consulta parametrizada, los caracteres especiales como `'` y `--` son tratados como parte del valor literal, no como elementos de la sintaxis SQL.

## Material Visual (para mostrar durante la explicación)

| Lo que intentamos | Lo que realmente sucede |
|-------------------|-------------------------|
| `SELECT * FROM usuarios WHERE username = '' OR 1=1 -- ' AND password = 'cualquiercosa'` | `SELECT * FROM usuarios WHERE username = ''' OR 1=1 --'` |

El motor de base de datos busca literalmente un usuario con nombre `' OR 1=1 --`, que no existe en la base de datos.

## Puntos a destacar

1. Django y otros frameworks modernos utilizan **consultas parametrizadas** por defecto
2. Nunca se construyen consultas SQL mediante concatenación de strings
3. Los caracteres especiales en las entradas del usuario se escapan automáticamente
4. Las entradas de usuario siempre se validan antes de procesarse

Esta demostración simple pero efectiva muestra cómo la aplicación está protegida contra uno de los ataques más comunes y peligrosos en aplicaciones web.
