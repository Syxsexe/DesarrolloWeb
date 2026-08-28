from django.shortcuts import render
from .models import NodoServidor

# Create your views here.
def listaServidores(request):
    servidores = NodoServidor.objects.all()
    context={'servidores': servidores}
    return render(request, 'infraestructura/index.html', context)
