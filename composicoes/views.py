from django.views.generic import TemplateView
from .models import Sicro, MaodeObraRelacaoComp, MaodeObraCusto, EquipamentoCusto, EquipamentoRelacaoComp, MaterialRelacaoComp, MaterialCusto, AtividadeAuxiliarRelacaoComp
from django.shortcuts import get_object_or_404
from django.db.models import F, OuterRef, Subquery, DecimalField, Sum
from django.db.models.functions import Cast


class MeuDetailView(TemplateView):
    template_name = "composicao.html"
    model = MaodeObraRelacaoComp

    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        estado = kwargs.get('estado')
        ano = kwargs.get('ano')
        mes = kwargs.get('mes')
        desonerado = kwargs.get('des')
        

        context = super().get_context_data(**kwargs)
        # context['composicao'] = objeto_composicao
        comp = get_comp(pk, estado, ano, mes, desonerado)

        context['comp'] = comp

        return context
    

def get_comp(pk, estado, ano, mes, desonerado, quantidade=None, item_tempo_fixo=None):
    objeto_composicao = get_object_or_404(Sicro, pk=pk)
    comp = {}
    if quantidade:
        comp['quantidade'] = quantidade
    if item_tempo_fixo:
        comp['item_tempo_fixo'] = item_tempo_fixo.codigo
        comp['descricao_item_tempo_fixo'] = item_tempo_fixo.descricao
    comp['descricao'] = objeto_composicao.descricao
    comp['codigo'] = pk
    comp['produtividade'] = objeto_composicao.produtividade
    comp['unidade'] = objeto_composicao.unidade

    
    custos_equipamentos = EquipamentoCusto.objects.filter(
        ano=ano, mes=mes, estado=estado, desonerado=desonerado,
        codigo=OuterRef('codigo')
    ).values('custo_produtivo', 'custo_improdutivo')
    
    equipamentos = EquipamentoRelacaoComp.objects.filter(
        comp=pk
    ).select_related('codigo').annotate(
        custo_produtivo = Subquery(custos_equipamentos.values('custo_produtivo')[:1]),
        custo_improdutivo = Subquery(custos_equipamentos.values('custo_improdutivo')[:1]),
        custo_horario_total = Cast(F('quantidade') *
                                    (F('utilizacao_operativa') * Subquery(custos_equipamentos.values('custo_produtivo')[:1]) +
                                    F('utilizacao_improdutiva') * Subquery(custos_equipamentos.values('custo_improdutivo')[:1])),
                                    DecimalField(max_digits=12, decimal_places=4)
                                    )
    )
    custo_equipamentos = equipamentos.aggregate(
        custo_total=Sum('custo_horario_total')
        )
    if not custo_equipamentos['custo_total']:
        custo_equipamentos['custo_total'] = 0

    comp['equipamento'] = equipamentos
    comp['custototalequipamentos'] = custo_equipamentos['custo_total']

    custos_mao_de_obra = MaodeObraCusto.objects.filter(
        ano=ano, mes=mes, estado=estado, desonerado=desonerado,
        codigo=OuterRef('codigo')
    ).values('custo')
    maos_de_obra = MaodeObraRelacaoComp.objects.filter(
        comp=pk
    ).select_related('codigo').annotate(
        preco=Subquery(custos_mao_de_obra[:1]),
        preco_total=Cast(F('quantidade') * Subquery(custos_mao_de_obra[:1]), 
                            DecimalField(max_digits=12, decimal_places=4)
                            )
        )
    custo_mao_de_obra = maos_de_obra.aggregate(
        custo_total=Sum('preco_total')
        )
    if not custo_mao_de_obra['custo_total']:
        custo_mao_de_obra['custo_total'] = 0

    comp['mao_de_obra'] = maos_de_obra
    comp['custototalmaodeobra'] = custo_mao_de_obra['custo_total']

    custos_materiais = MaterialCusto.objects.filter(
        ano=ano, mes=mes, estado=estado, desonerado=desonerado,
        codigo=OuterRef('codigo')
    ).values('preco_unitario')
    materiais = MaterialRelacaoComp.objects.filter(
        comp=pk
    ).select_related('codigo').annotate(
        preco=Subquery(custos_materiais[:1]),
        preco_total=Cast(F('quantidade') * Subquery(custos_materiais[:1]),
                            DecimalField(max_digits=12, decimal_places=4)
                            )
        )
    custo_materiais = materiais.aggregate(
        custo_total=Sum('preco_total')
        )
    if not custo_materiais['custo_total']:
        custo_materiais['custo_total'] = 0
    
    if materiais:
        comp['tempo_fixo'] = []
        for material in materiais:
            if material.tempo_fixo:
                quantidade = material.quantidade_tempo_fixo
                comp['tempo_fixo'].append(get_comp(material.tempo_fixo.codigo, estado, ano, mes, desonerado, quantidade, material.codigo))

    else:
        comp['custotempofixo'] = 0

    comp['material'] = materiais
    
    custoequipmobra = custo_equipamentos['custo_total'] + custo_mao_de_obra['custo_total']
    comp['custoequipmobra'] = custoequipmobra
    custounitariodeexecucao = round(custoequipmobra / objeto_composicao.produtividade, 4)
    # precisa alterar essa parte, porque o fic varia de acordo com o estado
    custo_fic = round(objeto_composicao.fic * custounitariodeexecucao, 4)
    comp['custo_fic'] = custo_fic
    comp['custounitariodeexecucao'] = custounitariodeexecucao
    comp['custototalmateriais'] = custo_materiais['custo_total']

    ativ_auxiliares = AtividadeAuxiliarRelacaoComp.objects.filter(codigo=pk)
    if ativ_auxiliares:
        comp['ativ_auxiliares'] = []
        for ativ_auxiliar in ativ_auxiliares:
            quantidade = ativ_auxiliar.quantidade
            comp['ativ_auxiliares'].append(get_comp(ativ_auxiliar.atividade_aux.codigo, estado, ano, mes, desonerado, quantidade))
            if ativ_auxiliar.tempo_fixo:
                quantidade = ativ_auxiliar.quantidade_tempo_fixo
                if not 'tempo_fixo' in comp:
                    comp['tempo_fixo'] = []
                comp['tempo_fixo'].append(get_comp(ativ_auxiliar.tempo_fixo.codigo, estado, ano, mes, desonerado, quantidade, ativ_auxiliar.codigo))
        comp['custoativauxiliares'] = 0
        for ativ_auxiliar in comp['ativ_auxiliares']:
            custounitaux = round(ativ_auxiliar['quantidade'] * ativ_auxiliar['custototal'], 4)
            ativ_auxiliar['custounitaux'] = custounitaux
            comp['custoativauxiliares'] += custounitaux
    else:
        comp['custoativauxiliares'] = 0
    
    if 'tempo_fixo' in comp:
        comp['custotempofixo'] = 0
        for tempo_fixo in comp['tempo_fixo']:
            custo_unit_tempofixo = round(tempo_fixo['quantidade'] * tempo_fixo['custototal'],4)
            tempo_fixo['custounittempofixo'] = custo_unit_tempofixo
            comp['custotempofixo'] += custo_unit_tempofixo
    else:
        comp['custotempofixo'] = 0

    subtotal = custounitariodeexecucao + custo_materiais['custo_total'] + comp['custoativauxiliares'] + comp['custo_fic']
    comp['subtotal'] = subtotal
    comp['custototal'] = round(subtotal + comp['custotempofixo'], 2)

    return comp