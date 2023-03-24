from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Estado, Obra

from django.urls import reverse_lazy

# Create your views here.

class ObraCreate(CreateView):
    model = Obra
    fields = ['nome', 'ano', 'tipo_de_obra', 'estado']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-obras')

class ObraUpdate(UpdateView):
    model = Obra
    fields = ['nome', 'ano', 'tipo_de_obra', 'estado']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-obras')

class ObraDelete(DeleteView):
    model = Obra
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('listar-obras')

class ObraList(ListView):
    model = Obra
    template_name = 'listas/obra.html'

