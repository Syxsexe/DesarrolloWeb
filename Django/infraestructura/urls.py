from django.urls import path
from .views import (
    listaServidores, detalleServidor, crear_servidor, editar_servidor, eliminar_servidor,
    crear_incidencia, resolver_incidencia,
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

]
