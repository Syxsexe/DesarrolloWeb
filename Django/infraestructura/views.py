from django.shortcuts import get_object_or_404, render, redirect
from .forms import NodoServidorForm
from .models import NodoServidor

def eliminar_servidor(request, pk):
    nodo = get_object_or_404(NodoServidor, pk=pk)
    if request.method == 'POST':
        nodo.delete()
        return redirect('home_servidores')
    return render(request, 'infraestructura/eliminar_servidor.html', {'nodo': nodo})

def editar_servidor(request, pk):
    nodo = get_object_or_404(NodoServidor, pk=pk)
    if request.method == 'POST':
        form = NodoServidorForm(request.POST, instance=nodo)
        if form.is_valid():
            form.save()
            return redirect('detalle_servidor', pk=nodo.pk)
    else:
        form = NodoServidorForm(instance=nodo)
    return render(request, 'infraestructura/editar_servidor.html', {'form': form, 'nodo': nodo})

def crear_servidor(request):
    if request.method == 'POST':
        form = NodoServidorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_servidores')
    else:
        form = NodoServidorForm()
    return render(request, 'infraestructura/crear_servidor.html', {'form': form})

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

