from django.urls import path
from .views import listaServidores, detalleServidor,crear_servidor,editar_servidor,eliminar_servidor


urlpatterns = [

    path('', listaServidores, name='HomeServers'),
    path('servidor/<int:pk>/', detalleServidor, name='detalle_servidor'),
    path('servidor/nuevo/', crear_servidor, name='crear_servidor'),
    path('servidor/<int:pk>/editar/', editar_servidor, name='editar_servidor'),
    path('servidor/<int:pk>/eliminar/', eliminar_servidor, name='eliminar_servidor'),

]
