from django import forms
from .models import NodoServidor, IncidenciaServidor

class NodoServidorForm(forms.ModelForm):
    """ModelForm de alta/edición de nodos, con clases Bootstrap en cada widget.

    Sin esto, Django renderiza <input>/<select> "pelados" (sin form-control
    ni form-select), que se ven fuera de lugar dentro de una tarjeta Bootstrap:
    de ahí la necesidad de declarar los widgets explícitamente en vez de
    dejar que ModelForm los infiera solo del tipo de campo del modelo.
    """

    class Meta:
        model = NodoServidor
        fields = ['nombre_host', 'direccion_ip', 'motor_contenedores', 'proxy_inverso', 'en_produccion']
        widgets = {
            'nombre_host': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: nodo-prod-01.udenarnova.local',
            }),
            'direccion_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 10.10.5.5',
            }),
            'motor_contenedores': forms.Select(attrs={'class': 'form-select'}),
            # form-check-input (en vez de form-control) es la clase que
            # Bootstrap espera específicamente en checkboxes/switches; los
            # booleanos del modelo se renderizan como CheckboxInput por
            # defecto, solo hace falta ponerle la clase correcta.
            'proxy_inverso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'en_produccion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


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
