from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist

from .models import Obra, CompsObra
from composicoes.models import Sicro

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


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


class ObraCompsImportadas(TemplateView):
    template_name = 'obra_tabs/tab-comps-importadas.html'


def att_comps_obra(request):
    if request.method == 'POST':
        # Obtém a lista de códigos enviada no corpo da requisição
        codigos = request.POST.getlist('codigos[]')
        # Obtém o valor da variável id correspondente ao id da obra
        obra_id = request.POST.get('obra')

        try:
            # Obtém a instância de Obra correspondente ao id
            obra = Obra.objects.get(id=obra_id)
        except ObjectDoesNotExist:
            return JsonResponse({'erro': 'Obra não encontrada.'}, status=400)

        # Processar os códigos e adicionar à coluna 'codigo' da Tabela CompsObra
        for codigo_id in codigos:
            try:
                # Obtpem a instância de composição correspondente ao codigo
                codigo = Sicro.objects.get(codigo=codigo_id)
            except ObjectDoesNotExist:
                return JsonResponse({'erro': 'Composição não encontrada.'}, status=400)
            if not CompsObra.objects.filter(composicao=codigo, obra=obra).exists():
                CompsObra.objects.create(composicao=codigo, obra=obra)

        return JsonResponse({'mensagem': 'Códigos adicionados com sucesso.'})

    elif request.method == 'DELETE':
        # Obtém a lista de códigos enviadas no corpo da requisição
        codigos = request.POST.getlist('codigos[]')
        # Obtém o valor da variável id correspondente ao id da obra
        obra_id = request.POST.get('obra')

        try:
            # Obtém a instância de Obra correspondente ao id
            obra = Obra.objects.get(id=obra_id)
        except ObjectDoesNotExist:
            return JsonResponse({'erro': 'Obra não encontrada.'}, status=400)

        # Exclui os objetos de CompsObra de uma só vez
        CompsObra.objects.filter(composicao__in=codigos, obra=obra).delete()

        # Retornar uma resposta de sucesso
        return JsonResponse({'mensagem': 'Códigos excluídos com sucesso'})

    else:
        return JsonResponse({'erro': "Método inválido"}, status=400)
