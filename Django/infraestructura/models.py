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
