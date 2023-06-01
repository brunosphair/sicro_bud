from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Obra

from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404

# Create your views here.


class ObraCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Obra
    fields = ['nome', 'mes', 'ano', 'tipo_de_obra', 'estado']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-obras')

    def form_valid(self, form):

        form.instance.usuario = self.request.user

        url = super().form_valid(form)

        return url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["titulo"] = "Cadastro de Obra"
        context["botao"] = "Cadastrar"
        return context


class ObraUpdate(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Obra
    fields = ['nome', 'mes', 'ano', 'tipo_de_obra', 'estado']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-obras')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Obra, pk=self.kwargs['pk'], usuario=self.request.user)
        return self.object

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["titulo"] = "Editar cadastro de Obra"
        context["botao"] = "Salvar"
        return context


class ObraDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Obra
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('listar-obras')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Obra, pk=self.kwargs['pk'], usuario=self.request.user)
        return self.object


class ObraList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Obra
    template_name = 'listas/obra.html'

    def get_queryset(self):
        self.object_list = Obra.objects.filter(usuario=self.request.user)
        return self.object_list


class TesteObra(TemplateView):
    template_name = 'listas/test.html'
