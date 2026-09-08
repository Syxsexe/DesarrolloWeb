# DesarrolloWeb

Repo para clases de Desarrollo Web con Django.

El proyecto es **centro_comando**: un panel de gestión de una flota de
servidores, con su app `infraestructura`. Ofrece dos interfaces sobre los
mismos datos: vistas HTML con plantillas Bootstrap y una API REST en JSON.

## Puesta en marcha

Todos los comandos se ejecutan desde el directorio `Django/` (el que
contiene `manage.py`).

```bash
cd Django

# 1. Entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS

# 2. Dependencias
pip install -r requirements.txt

# 3. Base de datos (SQLite local, no se versiona)
python manage.py migrate

# 4. Usuario para el admin y para escribir vía API
python manage.py createsuperuser

# 5. Servidor de desarrollo
python manage.py runserver
```

Queda en http://127.0.0.1:8000/.

## Modelos

| Modelo | Descripción |
| --- | --- |
| `NodoServidor` | Un servidor de la flota. Su IP se valida contra las subredes corporativas autorizadas (`10.10.0.0/16`, `10.20.0.0/16`, `172.16.8.0/22`). |
| `RegistroAuditoria` | Bitácora de eventos de un nodo. Solo crece: no se edita ni se borra. |
| `IncidenciaServidor` | Fallo operativo de un nodo. Nace `abierta` y se cierra como `resuelta`. |

## Interfaz HTML

| Ruta | Vista |
| --- | --- |
| `/` | Listado de la flota |
| `/servidor/<pk>/` | Ficha del nodo con su bitácora e incidencias |
| `/servidor/nuevo/` · `/servidor/<pk>/editar/` · `/servidor/<pk>/eliminar/` | Alta, edición y baja |
| `/servidor/<pk>/incidencias/nueva/` | Reportar una incidencia |
| `/incidencia/<pk>/resolver/` | Cerrar una incidencia (solo POST) |
| `/admin/` | Admin de Django |

## API REST

Construida con Django REST Framework. La API navegable se explora desde el
propio navegador entrando a `/api/`.

| Ruta | Métodos |
| --- | --- |
| `/api/` | Índice de endpoints |
| `/api/servidores/` · `/api/servidores/<pk>/` | CRUD completo |
| `/api/servidores/<pk>/auditorias/` | GET |
| `/api/servidores/<pk>/incidencias/` | GET (admite `?estado=`) |
| `/api/auditorias/` · `/api/auditorias/<pk>/` | Solo GET y POST |
| `/api/incidencias/` · `/api/incidencias/<pk>/` | CRUD |
| `/api/incidencias/<pk>/resolver/` | POST |
| `/api-auth/login/` | Login para la API navegable |

**Permisos:** lectura abierta, escritura solo para usuarios autenticados
(`IsAuthenticatedOrReadOnly`). Para probar POST/PUT/DELETE desde el
navegador hay que iniciar sesión en `/api-auth/login/` o en `/admin/`.

**Paginación:** 20 resultados por página (`?page=2`).

**Filtros:** `?search=` y `?ordering=` en todos los listados; además
`?en_produccion=` y `?motor=` en servidores, `?servidor=` en auditorías, y
`?servidor=`, `?estado=`, `?severidad=` en incidencias.

Dos reglas del diseño de la API conviene tenerlas presentes:

- El campo `estado` de una incidencia es de **solo lectura**. Un
  `PATCH {"estado": "resuelta"}` no la cierra; hay que usar
  `POST /api/incidencias/<pk>/resolver/`, que además sella
  `fecha_resolucion`. Así no puede existir una incidencia resuelta sin
  fecha de cierre.
- La bitácora de auditoría acepta POST pero rechaza PUT/PATCH/DELETE con
  un 405: un registro de evidencia que se puede reescribir no sirve de
  evidencia.

## Estructura

```
Django/
├── manage.py
├── requirements.txt
├── centro_comando/          # Configuración del proyecto
│   ├── settings.py
│   └── urls.py              # Enruta /admin/, /api/ y la raíz
└── infraestructura/         # App principal
    ├── models.py            # Los tres modelos y el validador de IP
    ├── admin.py             # Admin con acciones masivas
    ├── forms.py             # ModelForms con widgets Bootstrap
    ├── views.py             # Vistas HTML
    ├── urls.py              # Rutas HTML
    ├── serializers.py       # Serializers de la API
    ├── api_views.py         # ViewSets de la API
    ├── api_urls.py          # Router de la API
    └── templates/
```
