from django.urls import path
from .views import listaServidores

urlpatterns = [

    path('', listaServidores, name='HomeServers')

]