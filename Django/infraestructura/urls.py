from django.urls import path
from .views import listaServidores, detalleServidor

urlpatterns = [

    path('', listaServidores, name='HomeServers'),
    path('servidor/<int:pk>/', detalleServidor, name='DetalleServidor'),

]
