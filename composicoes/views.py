from django.views.generic import TemplateView
from .models import Sicro, SicroMaodeObra, SicroCustoMaodeObra
from django.shortcuts import get_object_or_404


class MeuDetailView(TemplateView):
    template_name = "composicao.html"
    model = SicroMaodeObra

    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        estado = kwargs.get('estado')
        ano = kwargs.get('ano')
        mes = kwargs.get('mes')
        objeto_composicao = get_object_or_404(Sicro, pk=pk)
        context = super().get_context_data(**kwargs)
        context['composicao'] = objeto_composicao
        objeto_mao_de_obra = SicroMaodeObra.objects.filter(comp = pk).select_related('codigo')
        codigos_mao_de_obra = []
        for mao_de_obra in objeto_mao_de_obra:
            codigos_mao_de_obra.append(mao_de_obra.codigo.codigo)
        custo_mao_de_obra = SicroCustoMaodeObra.objects.filter(estado=estado,
                                                               ano=ano,
                                                               mes=mes,
                                                               codigo__in=codigos_mao_de_obra)
        precos_dict = {}
        for custo in custo_mao_de_obra:
            precos_dict[custo.codigo_id] = custo.custo
        for mao_de_obra in objeto_mao_de_obra:
            codigo = mao_de_obra.codigo.codigo
            mao_de_obra.preco = precos_dict[codigo]
            mao_de_obra.preco_total = round(mao_de_obra.quantidade * precos_dict[codigo] * 10000) / 10000
        context['maodeobra'] = objeto_mao_de_obra
        return context