from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)
from .forms import NodoServidorForm, IncidenciaServidorForm, MantenimientoForm
from .models import NodoServidor, IncidenciaServidor, MantenimientoNodo

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


# --- CRUD de mantenimientos con Vistas Basadas en Clases (CBV) -------------
# Todo lo que arriba se escribe a mano (if request.method == 'POST',
# form.is_valid(), form.save(), el render final) lo resuelven por debajo
# las vistas genéricas de Django: aquí solo se declara QUÉ modelo, QUÉ
# formulario y QUÉ plantilla usar.

class MantenimientoListView(ListView):
    model = MantenimientoNodo
    template_name = 'infraestructura/mantenimiento_list.html'
    # Sin esto la plantilla recibiría el queryset como 'object_list' /
    # 'mantenimientonodo_list'; 'mantenimientos' se lee mucho mejor.
    context_object_name = 'mantenimientos'

    def get_queryset(self):
        # select_related trae el NodoServidor en el mismo JOIN: la plantilla
        # imprime m.servidor.nombre_host por cada fila y sin esto Django
        # lanzaría una consulta extra por mantenimiento (problema N+1).
        return super().get_queryset().select_related('servidor')


class MantenimientoDetailView(DetailView):
    model = MantenimientoNodo
    template_name = 'infraestructura/mantenimiento_detail.html'
    context_object_name = 'mantenimiento'


class MantenimientoCreateView(CreateView):
    model = MantenimientoNodo
    form_class = MantenimientoForm
    template_name = 'infraestructura/mantenimiento_form.html'
    # reverse_lazy (y no reverse) porque success_url se evalúa al importar
    # el módulo, cuando el registro de URLs todavía no está cargado.
    success_url = reverse_lazy('lista_mantenimientos')


class MantenimientoUpdateView(UpdateView):
    model = MantenimientoNodo
    form_class = MantenimientoForm
    # La misma plantilla que el alta: CreateView y UpdateView comparten
    # ModelFormMixin, así que ambas exponen 'form' en el contexto.
    template_name = 'infraestructura/mantenimiento_form.html'
    success_url = reverse_lazy('lista_mantenimientos')


class MantenimientoDeleteView(DeleteView):
    model = MantenimientoNodo
    template_name = 'infraestructura/mantenimiento_confirm_delete.html'
    success_url = reverse_lazy('lista_mantenimientos')
