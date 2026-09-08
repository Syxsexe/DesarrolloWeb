"""Rutas de la API REST, separadas de urls.py (que enruta las vistas HTML).

A diferencia de urls.py, aquí no se escribe un path() por operación: el
router recorre cada ViewSet y genera automáticamente el par de rutas del
CRUD junto con las de las @action declaradas.

Para NodoServidorViewSet, por ejemplo, produce:

    GET/POST        /api/servidores/
    GET/PUT/PATCH/DELETE  /api/servidores/<pk>/
    GET             /api/servidores/<pk>/auditorias/
    GET             /api/servidores/<pk>/incidencias/

DefaultRouter (y no SimpleRouter) porque añade además una vista índice en
/api/ que lista los endpoints disponibles, cómoda para explorar la API
desde el navegador.
"""

from rest_framework.routers import DefaultRouter

from .api_views import (
    IncidenciaServidorViewSet,
    NodoServidorViewSet,
    RegistroAuditoriaViewSet,
)

router = DefaultRouter()
# El primer argumento es el prefijo de la URL; basename lo usa DRF para
# nombrar las rutas generadas (p. ej. 'servidor-detail' en un reverse()).
router.register(r'servidores', NodoServidorViewSet, basename='servidor')
router.register(r'auditorias', RegistroAuditoriaViewSet, basename='auditoria')
router.register(r'incidencias', IncidenciaServidorViewSet, basename='incidencia')

urlpatterns = router.urls
