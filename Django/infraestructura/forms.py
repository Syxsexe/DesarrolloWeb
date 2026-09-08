from django import forms
from .models import NodoServidor, IncidenciaServidor

class NodoServidorForm(forms.ModelForm):
    class Meta:
        model = NodoServidor
        fields = ['nombre_host', 'direccion_ip', 'motor_contenedores', 'proxy_inverso', 'en_produccion']


class IncidenciaServidorForm(forms.ModelForm):
    """Formulario de alta de incidencias, con clases Bootstrap en cada widget.

    'servidor' y 'estado' quedan fuera de `fields` a propósito:
    - servidor se asigna en la vista a partir del pk de la URL (el usuario
      ya está parado en la ficha del nodo, no tiene sentido pedírselo de nuevo).
    - estado siempre nace en 'abierta' (valor default del modelo); pasar a
      'resuelta' es una acción separada (ver resolver_incidencia en views.py),
      no algo que se declare al momento de reportar el fallo.
    """

    class Meta:
        model = IncidenciaServidor
        fields = ['titulo', 'descripcion', 'severidad']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Caída del servicio Nginx',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el fallo observado, su impacto y contexto relevante.',
            }),
            'severidad': forms.Select(attrs={'class': 'form-select'}),
        }
