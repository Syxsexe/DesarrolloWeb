from django.contrib import admin, messages
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

    # Acciones masivas disponibles en el desplegable del listado
    actions = ('marcar_como_produccion', 'marcar_como_mantenimiento')

    @admin.action(description="Activar Producción Masiva")
    def marcar_como_produccion(self, request, queryset):
        """Pone en producción (en_produccion=True) los nodos seleccionados."""
        actualizados = queryset.filter(en_produccion=False).update(en_produccion=True)
        if actualizados:
            self.message_user(
                request,
                f"{actualizados} nodo(s) puestos en producción correctamente.",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "Ningún cambio: los nodos seleccionados ya estaban en producción.",
                messages.INFO,
            )

    @admin.action(description="Poner en Mantenimiento")
    def marcar_como_mantenimiento(self, request, queryset):
        """Aísla los nodos seleccionados (en_produccion=False)."""
        actualizados = queryset.filter(en_produccion=True).update(en_produccion=False)
        if actualizados:
            self.message_user(
                request,
                f"{actualizados} nodo(s) retirados de producción y puestos en mantenimiento.",
                messages.WARNING,
            )
        else:
            self.message_user(
                request,
                "Ningún cambio: los nodos seleccionados ya estaban en mantenimiento.",
                messages.INFO,
            )
