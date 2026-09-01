from django.shortcuts import get_object_or_404, render

from .models import NodoServidor


# Create your views here.
def listaServidores(request):
    servidores = NodoServidor.objects.all()
    context={'servidores': servidores}
    return render(request, 'infraestructura/index.html', context)


def detalleServidor(request, pk):
    """Ficha completa de un nodo junto con su bitácora de auditoría."""
    # get_object_or_404 devuelve el nodo o lanza un 404 limpio si el pk no
    # existe, en vez de reventar con DoesNotExist.
    servidor = get_object_or_404(NodoServidor, pk=pk)
    # related_name='auditorias' en el FK permite recorrer los eventos del
    # nodo; el Meta del modelo ya los ordena del más reciente al más antiguo.
    context = {
        'servidor': servidor,
        'auditorias': servidor.auditorias.all(),
    }
    return render(request, 'infraestructura/detalle.html', context)
