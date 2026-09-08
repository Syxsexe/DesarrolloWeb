from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from .forms import NodoServidorForm, IncidenciaServidorForm
from .models import NodoServidor, IncidenciaServidor

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
        # related_name='incidencias' del FK en IncidenciaServidor: mismo
        # patrón que 'auditorias', ya ordenado por el Meta del modelo.
        'incidencias': servidor.incidencias.all(),
    }
    return render(request, 'infraestructura/detalle.html', context)


def crear_incidencia(request, pk):
    """Registra una nueva incidencia sobre un NodoServidor puntual.

    El pk de la URL identifica el servidor afectado; por eso 'servidor' no
    forma parte de IncidenciaServidorForm (ver forms.py): se resuelve aquí
    y se asigna a mano antes de guardar.
    """
    servidor = get_object_or_404(NodoServidor, pk=pk)
    if request.method == 'POST':
        form = IncidenciaServidorForm(request.POST)
        if form.is_valid():
            # commit=False construye la instancia en memoria sin tocar la
            # base de datos todavía, para poder completar 'servidor' (que
            # el form no conoce) antes del guardado real.
            incidencia = form.save(commit=False)
            incidencia.servidor = servidor
            incidencia.save()
            return redirect('detalle_servidor', pk=servidor.pk)
    else:
        form = IncidenciaServidorForm()
    return render(
        request,
        'infraestructura/crear_incidencia.html',
        {'form': form, 'servidor': servidor},
    )


def resolver_incidencia(request, pk):
    """Cierra una incidencia: la pasa a 'resuelta' y sella la fecha.

    Se exige POST (nunca GET) porque es una acción que muta estado; un
    enlace <a> con GET dejaría la incidencia expuesta a cierres accidentales
    por prefetch del navegador o por un simple clic sin confirmación.
    """
    incidencia = get_object_or_404(IncidenciaServidor, pk=pk)
    if request.method == 'POST':
        incidencia.estado = 'resuelta'
        incidencia.fecha_resolucion = timezone.now()
        incidencia.save()
    return redirect('detalle_servidor', pk=incidencia.servidor.pk)

