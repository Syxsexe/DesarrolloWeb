import ipaddress

from django.core.exceptions import ValidationError
from django.db import models


# --- Política de subredes corporativas -------------------------------------
# Únicos rangos privados donde la empresa permite dar de alta un nodo.
SUBREDES_CORPORATIVAS = [
    ipaddress.ip_network('10.10.0.0/16'),    # Núcleo de producción
    ipaddress.ip_network('10.20.0.0/16'),    # Staging / preproducción
    ipaddress.ip_network('172.16.8.0/22'),   # DMZ y balanceadores
]

SUBREDES_VETADAS = [
    ipaddress.ip_network('192.168.100.0/24'),  # Laboratorio de aislamiento
]


def validar_ip_corporativa(value):
    """Rechaza IPs reservadas y rangos privados fuera de la política de red."""
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        raise ValidationError("La dirección IP no tiene un formato válido.")

    if ip.is_loopback:
        raise ValidationError(
            "Las direcciones de loopback (127.0.0.0/8) no identifican un nodo de la flota."
        )
    if ip.is_link_local:
        raise ValidationError(
            "Las direcciones link-local (169.254.0.0/16) indican fallo de DHCP y no son enrutables."
        )
    if ip.is_multicast:
        raise ValidationError("Las direcciones multicast no pueden asignarse a un nodo de servidor.")
    if ip.is_unspecified:
        raise ValidationError("La dirección no especificada (0.0.0.0) no es un destino válido.")
    if ip.is_reserved:
        raise ValidationError(f"El rango de {ip} está reservado por la IANA y no puede registrarse.")

    for red in SUBREDES_VETADAS:
        if ip.version == red.version and ip in red:
            raise ValidationError(
                f"Las direcciones IP en el segmento {red} están reservadas "
                "para pruebas internas de aislamiento."
            )
        
    if ip.is_private:
        permitida = any(
            ip.version == red.version and ip in red for red in SUBREDES_CORPORATIVAS
        )
        if not permitida:
            rangos = ", ".join(str(red) for red in SUBREDES_CORPORATIVAS)
            raise ValidationError(
                f"{ip} pertenece a un rango privado no autorizado. "
                f"Las subredes corporativas habilitadas son: {rangos}."
            )


class NodoServidor(models.Model):
    # Opciones predefinidas para el panel
    MOTORES_CONTENEDOR = [
        ('docker', 'Docker'),
        ('podman', 'Podman'),
        ('lxc', 'LXC Linux Containers'),
        ('ninguno', 'Sin contenedores'),
    ]

    nombre_host = models.CharField(max_length=100, unique=True, verbose_name="Hostname")
    direccion_ip = models.GenericIPAddressField(
        verbose_name="Dirección IP",
        validators=[validar_ip_corporativa],
        help_text="Debe pertenecer a una subred corporativa autorizada (10.10.0.0/16, 10.20.0.0/16, 172.16.8.0/22).",
    )
    motor_contenedores = models.CharField(
        max_length=20,
        choices=MOTORES_CONTENEDOR,
        default='podman',
        verbose_name="Motor de Contenedores"
    )
    proxy_inverso = models.BooleanField(default=True, verbose_name="¿Enrutado por Nginx?")
    en_produccion = models.BooleanField(default=True, verbose_name="Estado Producción")
    fecha_despliegue = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_host} [{self.direccion_ip}]"

    class Meta:
        verbose_name = "Nodo de Servidor"
        verbose_name_plural = "Flota de Servidores"


class RegistroAuditoria(models.Model):
    """Bitácora de eventos críticos ocurridos sobre un NodoServidor."""

    # Relación de llave foránea (FK) hacia NodoServidor: cada registro de
    # auditoría pertenece a UN servidor, pero un servidor puede tener MUCHOS
    # registros de auditoría (relación uno-a-muchos).
    servidor = models.ForeignKey(
        NodoServidor,
        # on_delete=CASCADE indica que si se elimina el NodoServidor,
        # Django borrará en cascada todos sus registros de auditoría
        # asociados (no quedan registros "huérfanos" apuntando a un
        # servidor inexistente).
        on_delete=models.CASCADE,
        # related_name='auditorias' permite acceder desde una instancia de
        # NodoServidor a todos sus eventos con la sintaxis
        # nodo.auditorias.all(), en vez del nombre por defecto que
        # generaría Django (registroauditoria_set).
        related_name='auditorias',
        verbose_name="Servidor Afectado",
    )

    # TextField (a diferencia de CharField) no exige una longitud máxima,
    # apropiado para descripciones de eventos que pueden ser extensas.
    detalles = models.TextField(verbose_name="Detalle del Evento")

    # auto_now_add=True hace que Django asigne la fecha/hora actual
    # automáticamente SOLO al crear el registro (no se puede editar
    # después ni se actualiza en modificaciones posteriores). Es distinto
    # de auto_now=True, que se actualizaría en cada guardado.
    fecha_evento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Evento")

    def __str__(self):
        # Representación legible en el admin y en el shell de Django:
        # combina el servidor afectado con la fecha del evento.
        return f"[{self.fecha_evento:%Y-%m-%d %H:%M}] {self.servidor.nombre_host}"

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Historial de Auditoría"
        # Ordena los registros del más reciente al más antiguo por defecto.
        ordering = ('-fecha_evento',)


class IncidenciaServidor(models.Model):
    """Fallos y alertas operativas reportadas sobre un NodoServidor.

    A diferencia de RegistroAuditoria (una bitácora de solo lectura que
    crece con el tiempo), una incidencia tiene un ciclo de vida: nace
    'abierta' y en algún momento se marca como 'resuelta', por lo que
    necesita campos mutables (estado, fecha_resolucion) además de los
    de registro.
    """

    # Los choices se guardan como el primer valor (clave interna, estable
    # aunque cambie el texto) y se muestran con el segundo (etiqueta legible).
    # Mantener las claves en minúscula evita choques con mayúsculas si en el
    # futuro se comparan strings manualmente en vistas o templates.
    SEVERIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('resuelta', 'Resuelta'),
    ]

    # Igual que en RegistroAuditoria: relación uno-a-muchos hacia
    # NodoServidor. related_name='incidencias' habilita
    # nodo.incidencias.all() desde una instancia de NodoServidor.
    servidor = models.ForeignKey(
        NodoServidor,
        on_delete=models.CASCADE,
        related_name='incidencias',
        verbose_name="Servidor Afectado",
    )

    titulo = models.CharField(max_length=150, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción del Fallo")

    severidad = models.CharField(
        max_length=10,
        choices=SEVERIDAD_CHOICES,
        default='media',
        verbose_name="Severidad",
    )

    # No se usa un BooleanField (ej. resuelto=True/False) porque el
    # enunciado pide un "estado de resolución": un CharField con choices
    # deja la puerta abierta a más estados futuros (ej. 'en_progreso')
    # sin tener que migrar el tipo de dato.
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='abierta',
        verbose_name="Estado de Resolución",
    )

    # auto_now_add=True: se fija una sola vez, al crear la incidencia.
    fecha_reporte = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reporte")

    # null=True/blank=True porque en el momento de crear la incidencia
    # todavía no está resuelta; el valor se completa después, cuando la
    # vista de resolución la marca como 'resuelta'.
    fecha_resolucion = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Resolución"
    )

    def __str__(self):
        return f"[{self.get_severidad_display()}] {self.titulo} — {self.servidor.nombre_host}"

    class Meta:
        verbose_name = "Incidencia de Servidor"
        verbose_name_plural = "Incidencias de Servidores"
        # Las incidencias más recientes (y presumiblemente las que aún
        # requieren atención) aparecen primero en cualquier listado.
        ordering = ('-fecha_reporte',)
