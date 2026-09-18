from django.urls import path
from .views import (
    listaServidores, detalleServidor, crear_servidor, editar_servidor, eliminar_servidor,
    crear_incidencia, resolver_incidencia,
    MantenimientoListView, MantenimientoDetailView,
    MantenimientoCreateView, MantenimientoUpdateView, MantenimientoDeleteView,
)


urlpatterns = [

    path('', listaServidores, name='home_servidores'),
    path('servidor/<int:pk>/', detalleServidor, name='detalle_servidor'),
    path('servidor/nuevo/', crear_servidor, name='crear_servidor'),
    path('servidor/<int:pk>/editar/', editar_servidor, name='editar_servidor'),
    path('servidor/<int:pk>/eliminar/', eliminar_servidor, name='eliminar_servidor'),

    # El pk aquí es el del NodoServidor (no el de la incidencia): se llega
    # desde la ficha de un servidor concreto para reportar un fallo suyo.
    path('servidor/<int:pk>/incidencias/nueva/', crear_incidencia, name='crear_incidencia'),
    # Este pk sí es el de la IncidenciaServidor a cerrar; la vista resuelve
    # sola a qué servidor pertenece para redirigir de vuelta a su detalle.
    path('incidencia/<int:pk>/resolver/', resolver_incidencia, name='resolver_incidencia'),

    # CRUD de mantenimientos (CBV). A diferencia de las vistas basadas en
    # funciones de arriba, aquí se enruta la CLASE: .as_view() la convierte
    # en el callable que Django espera recibir en cada path.
    path('mantenimientos/', MantenimientoListView.as_view(), name='lista_mantenimientos'),
    path('mantenimientos/nuevo/', MantenimientoCreateView.as_view(), name='crear_mantenimiento'),
    # 'nuevo/' va antes que '<int:pk>/' porque Django resuelve los patrones
    # en orden; aun siendo tipos distintos, mantener lo estático arriba
    # evita sorpresas al añadir rutas nuevas.
    path('mantenimientos/<int:pk>/', MantenimientoDetailView.as_view(), name='detalle_mantenimiento'),
    path('mantenimientos/<int:pk>/editar/', MantenimientoUpdateView.as_view(), name='editar_mantenimiento'),
    path('mantenimientos/<int:pk>/eliminar/', MantenimientoDeleteView.as_view(), name='eliminar_mantenimiento'),
]
