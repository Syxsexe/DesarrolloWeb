from django import forms
from .models import NodoServidor, IncidenciaServidor, MantenimientoNodo

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


class MantenimientoForm(forms.ModelForm):
    """Formulario del CRUD de mantenimientos, reutilizado por Create y Update.

    Aquí sí se incluye 'servidor' en `fields` (al contrario que en
    IncidenciaServidorForm): el alta de un mantenimiento se hace desde el
    listado general, no desde la ficha de un nodo, así que la URL no trae
    ningún pk de servidor del que deducirlo y el usuario debe elegirlo.

    'fecha_programada' usa type='datetime-local' para que el navegador
    muestre su selector nativo de fecha y hora en vez de un campo de texto.
    """

    class Meta:
        model = MantenimientoNodo
        fields = ['servidor', 'titulo_tarea', 'descripcion_tecnica', 'tipo',
                  'fecha_programada', 'completado']
        widgets = {
            'servidor': forms.Select(attrs={'class': 'form-select'}),
            'titulo_tarea': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Upgrade de kernel a 6.8 LTS',
            }),
            'descripcion_tecnica': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Pasos previstos, ventana estimada y plan de rollback.',
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_programada': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                # Sin format, el valor precargado al editar no coincide con
                # lo que espera datetime-local y el navegador deja el campo
                # vacío: hay que emitirlo en ISO y sin segundos.
                format='%Y-%m-%dT%H:%M',
            ),
            'completado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
