from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User
from .forms import UsuarioForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Perfil

# Create your views here.
class UsuarioCreate(CreateView):
    template_name = "form.html"
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        
        url= super().form_valid(form)

        Perfil.objects.create(usuario=self.object)

        return url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["titulo"] = "Registro de novo usuário"
        context["botao"] = "Cadastrar"

        return context
    
class PerfilUpdate(UpdateView):
    template_name = 'form.html'
    model = Perfil
    fields = ["nome", "sobrenome", "cpf", "telefone"]
    success_url = reverse_lazy('inicio')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Perfil, usuario=self.request.user)
        return self.object
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = 'Meus Dados'
        context['botao'] = 'Atualizar'

        return context