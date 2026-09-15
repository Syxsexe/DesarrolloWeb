"""Serializers de la API REST del centro de comando.

Un serializer hace en la API el papel que un ModelForm hace en las vistas
HTML (ver forms.py): valida la entrada y traduce entre instancias del
modelo y tipos primitivos de Python (que DRF convierte luego a JSON).

Nota importante sobre validaciones: ModelSerializer arrastra por sí solo
los validators declarados en el modelo, así que validar_ip_corporativa
sigue rechazando IPs fuera de las subredes autorizadas también cuando el
alta llega por la API, sin tener que repetir la regla aquí.
"""

from rest_framework import serializers

from .models import (
    IncidenciaServidor,
    MantenimientoNodo,
    NodoServidor,
    RegistroAuditoria,
)


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    """Bitácora de eventos de un nodo.

    Los campos con auto_now_add (fecha_evento) los marca DRF como de solo
    lectura automáticamente: no se pueden enviar en el POST.
    """

    # source='servidor.nombre_host' recorre el FK para exponer el hostname
    # legible junto al id numérico, evitando que el cliente tenga que pedir
    # /api/servidores/<id>/ solo para saber a qué nodo pertenece el evento.
    servidor_hostname = serializers.CharField(source='servidor.nombre_host', read_only=True)

    class Meta:
        model = RegistroAuditoria
        fields = ['id', 'servidor', 'servidor_hostname', 'detalles', 'fecha_evento']


class IncidenciaServidorSerializer(serializers.ModelSerializer):
    """Incidencias operativas de un nodo.

    'estado' y 'fecha_resolucion' quedan como read_only por la misma razón
    por la que IncidenciaServidorForm los excluye de sus fields: una
    incidencia nace siempre 'abierta' y se cierra mediante una acción
    explícita (POST /api/incidencias/<id>/resolver/), no editando el campo
    a mano. Así el sellado de fecha_resolucion nunca queda a criterio del
    cliente y no puede haber una incidencia 'resuelta' sin fecha.
    """

    servidor_hostname = serializers.CharField(source='servidor.nombre_host', read_only=True)
    # get_FOO_display() devuelve la etiqueta legible de un campo con
    # choices ('Crítica') en lugar de la clave interna ('critica').
    severidad_display = serializers.CharField(source='get_severidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = IncidenciaServidor
        fields = [
            'id', 'servidor', 'servidor_hostname', 'titulo', 'descripcion',
            'severidad', 'severidad_display', 'estado', 'estado_display',
            'fecha_reporte', 'fecha_resolucion',
        ]
        read_only_fields = ['estado', 'fecha_resolucion']


class MantenimientoNodoSerializer(serializers.ModelSerializer):
    """Tareas de mantenimiento programadas sobre un nodo.

    Aquí no hay campos de solo lectura más allá del id, al revés que en
    IncidenciaServidorSerializer: 'fecha_programada' la fija el operador al
    planificar la ventana (por eso el modelo no usa auto_now_add) y
    'completado' se marca con un PATCH normal cuando la tarea se ejecuta.
    No hace falta una @action como resolver() porque al cerrar un
    mantenimiento no queda ninguna fecha que sellar.
    """

    servidor_hostname = serializers.CharField(source='servidor.nombre_host', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = MantenimientoNodo
        fields = [
            'id', 'servidor', 'servidor_hostname', 'titulo_tarea',
            'descripcion_tecnica', 'tipo', 'tipo_display', 'completado',
            'fecha_programada',
        ]


class NodoServidorSerializer(serializers.ModelSerializer):
    """Representación de un nodo para los listados de la API."""

    motor_contenedores_display = serializers.CharField(
        source='get_motor_contenedores_display', read_only=True
    )
    # Contador de fallos pendientes, útil para pintar un semáforo en el
    # cliente sin descargar la lista completa de incidencias de cada nodo.
    incidencias_abiertas = serializers.SerializerMethodField()

    class Meta:
        model = NodoServidor
        fields = [
            'id', 'nombre_host', 'direccion_ip', 'motor_contenedores',
            'motor_contenedores_display', 'proxy_inverso', 'en_produccion',
            'fecha_despliegue', 'incidencias_abiertas',
        ]

    def get_incidencias_abiertas(self, obj) -> int:
        # El ViewSet ya anota este valor sobre el queryset con un único
        # COUNT agregado; el getattr lo aprovecha cuando está disponible y
        # solo cae al conteo por instancia (una consulta extra) si el
        # serializer se usa fuera de ese queryset anotado.
        anotado = getattr(obj, 'incidencias_abiertas', None)
        if anotado is not None:
            return anotado
        return obj.incidencias.filter(estado='abierta').count()


class NodoServidorDetalleSerializer(NodoServidorSerializer):
    """Ficha completa de un nodo: el equivalente en API de detalleServidor().

    Anida la bitácora y las incidencias del nodo (ambas de solo lectura)
    para que el detalle se resuelva en una sola petición, igual que la
    plantilla detalle.html las recibe juntas en su contexto. El listado
    general no las incluye porque haría enorme cada página de resultados.
    """

    auditorias = RegistroAuditoriaSerializer(many=True, read_only=True)
    incidencias = IncidenciaServidorSerializer(many=True, read_only=True)

    class Meta(NodoServidorSerializer.Meta):
        fields = NodoServidorSerializer.Meta.fields + ['auditorias', 'incidencias']
