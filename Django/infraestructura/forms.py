from django import forms
from .models import NodoServidor

class NodoServidorForm(forms.ModelForm):
    class Meta:
        model = NodoServidor
        #fields = ['nombre_host', 'direccion_ip', 'motor_contenedores', 'proxy_inverso', 'en_produccion']
        fields = ['nombre_host']