"""ViewSets de la API REST.

Se mantienen aparte de views.py a propósito: aquellas vistas renderizan
plantillas HTML y redirigen, mientras que estas devuelven JSON y no saben
nada de templates. Mezclarlas en un mismo archivo obligaría a leer dos
contratos distintos (respuesta renderizada vs. serializada) en el mismo
espacio de nombres.

Un ModelViewSet agrupa en una sola clase las seis operaciones CRUD
(list, create, retrieve, update, partial_update, destroy) que en el lado
HTML están repartidas en funciones sueltas (listaServidores,
crear_servidor, detalleServidor, editar_servidor, eliminar_servidor); el
router de api_urls.py es el que las mapea a URLs y verbos HTTP.
"""

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import IncidenciaServidor, NodoServidor, RegistroAuditoria
from .serializers import (
    IncidenciaServidorSerializer,
    NodoServidorDetalleSerializer,
    NodoServidorSerializer,
    RegistroAuditoriaSerializer,
)


class NodoServidorViewSet(viewsets.ModelViewSet):
    """CRUD completo de la flota de servidores."""

    # annotate() calcula el número de incidencias abiertas de cada nodo en
    # la misma consulta del listado. Sin esto, el serializer tendría que
    # contar por instancia y aparecería el clásico problema N+1: una
    # consulta extra por cada servidor de la página.
    queryset = NodoServidor.objects.annotate(
        incidencias_abiertas=Count(
            'incidencias', filter=Q(incidencias__estado='abierta')
        )
    )
    serializer_class = NodoServidorSerializer
    search_fields = ('nombre_host', 'direccion_ip')
    ordering_fields = ('nombre_host', 'fecha_despliegue', 'incidencias_abiertas')
    # Mismo orden por defecto que el admin: los despliegues más recientes
    # primero. NodoServidor no define ordering en su Meta, así que sin esta
    # línea la paginación podría devolver resultados en orden inestable.
    ordering = ('-fecha_despliegue',)

    def get_serializer_class(self):
        # El detalle de un nodo devuelve además su bitácora y sus
        # incidencias anidadas; el listado se queda en la versión ligera.
        if self.action == 'retrieve':
            return NodoServidorDetalleSerializer
        return NodoServidorSerializer

    def get_queryset(self):
        """Filtros simples por query string: ?en_produccion=&motor=."""
        queryset = super().get_queryset()
        params = self.request.query_params

        # Los query params llegan siempre como texto: en_produccion=false
        # es la cadena "false", que en Python es un valor verdadero. De ahí
        # la comparación explícita contra una lista de literales en vez de
        # un bool() directo, que dejaría pasar cualquier cosa como True.
        en_produccion = params.get('en_produccion')
        if en_produccion is not None:
            queryset = queryset.filter(
                en_produccion=en_produccion.lower() in ('1', 'true', 'si')
            )

        motor = params.get('motor')
        if motor:
            queryset = queryset.filter(motor_contenedores=motor)

        return queryset

    # detail=True cuelga la ruta del nodo concreto:
    # GET /api/servidores/<pk>/auditorias/
    @action(detail=True, methods=['get'])
    def auditorias(self, request, pk=None):
        """Bitácora del nodo, paginada e independiente de su ficha."""
        nodo = self.get_object()
        # related_name='auditorias' del FK; el Meta del modelo ya ordena
        # del evento más reciente al más antiguo.
        return self._respuesta_paginada(
            nodo.auditorias.all(), RegistroAuditoriaSerializer
        )

    @action(detail=True, methods=['get'])
    def incidencias(self, request, pk=None):
        """Incidencias del nodo; admite ?estado=abierta|resuelta."""
        nodo = self.get_object()
        incidencias = nodo.incidencias.all()

        estado = request.query_params.get('estado')
        if estado:
            incidencias = incidencias.filter(estado=estado)

        return self._respuesta_paginada(incidencias, IncidenciaServidorSerializer)

    def _respuesta_paginada(self, queryset, serializer_class):
        """Aplica al queryset la misma paginación configurada globalmente.

        Las @action no la heredan solas: hay que pasar por
        paginate_queryset() explícitamente, si no una ficha con miles de
        eventos devolvería todos de golpe en una sola respuesta.
        """
        pagina = self.paginate_queryset(queryset)
        if pagina is not None:
            serializer = serializer_class(pagina, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer_class(queryset, many=True).data)


class RegistroAuditoriaViewSet(viewsets.ModelViewSet):
    """Bitácora de auditoría de toda la flota.

    Se permite crear registros (para que un agente externo pueda reportar
    eventos), pero no editarlos ni borrarlos: una bitácora que se puede
    reescribir a posteriori no sirve como evidencia. De ahí que
    http_method_names recorte PUT/PATCH/DELETE en lugar de dejar el
    ModelViewSet completo.
    """

    # select_related('servidor') trae el nodo en la misma consulta con un
    # JOIN, porque el serializer expone servidor_hostname y sin esto cada
    # fila del listado dispararía una consulta adicional.
    queryset = RegistroAuditoria.objects.select_related('servidor')
    serializer_class = RegistroAuditoriaSerializer
    http_method_names = ['get', 'post', 'head', 'options']
    search_fields = ('detalles', 'servidor__nombre_host')
    ordering_fields = ('fecha_evento',)

    def get_queryset(self):
        """Filtro por nodo: ?servidor=<id>."""
        queryset = super().get_queryset()
        servidor = self.request.query_params.get('servidor')
        if servidor:
            queryset = queryset.filter(servidor_id=servidor)
        return queryset


class IncidenciaServidorViewSet(viewsets.ModelViewSet):
    """CRUD de incidencias más la acción de cierre.

    Recordar que el serializer marca 'estado' y 'fecha_resolucion' como de
    solo lectura: el ciclo de vida se mueve únicamente por la acción
    resolver(), nunca por un PATCH directo del campo.
    """

    queryset = IncidenciaServidor.objects.select_related('servidor')
    serializer_class = IncidenciaServidorSerializer
    search_fields = ('titulo', 'descripcion', 'servidor__nombre_host')
    ordering_fields = ('fecha_reporte', 'severidad')

    def get_queryset(self):
        """Filtros por ?servidor=<id>, ?estado= y ?severidad=."""
        queryset = super().get_queryset()
        params = self.request.query_params

        servidor = params.get('servidor')
        if servidor:
            queryset = queryset.filter(servidor_id=servidor)

        estado = params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        severidad = params.get('severidad')
        if severidad:
            queryset = queryset.filter(severidad=severidad)

        return queryset

    # Equivalente en API de resolver_incidencia() en views.py: solo POST,
    # porque muta estado. El router publica la ruta como
    # POST /api/incidencias/<pk>/resolver/
    @action(detail=True, methods=['post'])
    def resolver(self, request, pk=None):
        """Cierra la incidencia: la pasa a 'resuelta' y sella la fecha."""
        incidencia = self.get_object()

        if incidencia.estado == 'resuelta':
            # 409 Conflict y no 400: la petición está bien formada, lo que
            # falla es el estado actual del recurso.
            return Response(
                {'detail': 'La incidencia ya estaba resuelta.'},
                status=status.HTTP_409_CONFLICT,
            )

        incidencia.estado = 'resuelta'
        incidencia.fecha_resolucion = timezone.now()
        # update_fields limita el UPDATE a las dos columnas que cambian, en
        # vez de reescribir la fila entera.
        incidencia.save(update_fields=['estado', 'fecha_resolucion'])

        return Response(self.get_serializer(incidencia).data)
