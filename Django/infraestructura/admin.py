from django.contrib import admin

from django.contrib import admin
from .models import NodoServidor

@admin.register(NodoServidor)
class NodoServidorAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la tabla principal
    list_display = ('nombre_host', 'direccion_ip', 'motor_contenedores', 'proxy_inverso', 'en_produccion')

    # Filtros laterales para hacer búsquedas rápidas
    list_filter = ('motor_contenedores', 'proxy_inverso', 'en_produccion')

    # Barra de búsqueda superior
    search_fields = ('nombre_host', 'direccion_ip')

    # Orden por defecto
    ordering = ('-fecha_despliegue',)
