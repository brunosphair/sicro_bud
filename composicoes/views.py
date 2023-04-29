from django.views.generic import TemplateView
from .models import (
    Sicro, MaodeObraRelacaoComp, MaodeObraCusto,EquipamentoCusto,
    EquipamentoRelacaoComp, MaterialRelacaoComp, MaterialCusto,
    AtividadeAuxiliarRelacaoComp, CompFIC
)
from django.shortcuts import get_object_or_404
from django.db.models import F, OuterRef, Subquery, DecimalField, Sum
from django.db.models.functions import Cast


class MeuDetailView(TemplateView):
    template_name = "composicao.html"
    model = MaodeObraRelacaoComp

    def get_context_data(self, **kwargs):
        # obtencao das variaveis passadas na url
        pk = kwargs.get('pk')
        estado = kwargs.get('estado')
        ano = kwargs.get('ano')
        mes = kwargs.get('mes')
        desonerado = kwargs.get('des')
        
        context = super().get_context_data(**kwargs)
        comp = Composicao(pk, estado, ano, mes, desonerado)
        comp_data = comp.get_comp_all_data()

        context['comp'] = comp_data

        return context
    
class Composicao:
    def __init__(self, pk, estado, ano, mes, desonerado):
        '''
        Recebe o codigo da composicao como parametro e retorna um objeto com
        suas informacoes principais.
        '''
        self.obj_comp = get_object_or_404(Sicro, pk=pk)
        self.codigo = pk
        self.estado = estado
        self.ano = ano
        self.mes = mes
        self.desonerado = desonerado
        self.comp = {}
    
    def get_comp_all_data(self, quantidade=None, item_tempo_fixo=None):
        
        if quantidade:
            # Caso a quantidade seja passada como parametro, adiciona esse item
            # a composicao. Eh usado para tempo-fixo, ativ auxiliar e transporte.
            self.comp['quantidade'] = quantidade
        
        if item_tempo_fixo:
            # Caso a funcao tenha sido chamada para calcular tempo fixo, atribui
            # o codigo e a descricao do item que esta sendo transportado as
            # respectivas variaveis
            self.comp['item_tempo_fixo'] = item_tempo_fixo.codigo
            self.comp['descricao_item_tempo_fixo'] = item_tempo_fixo.descricao
        
        # Definicoes gerais da composicao
        self.comp['descricao'] = self.obj_comp.descricao
        self.comp['codigo'] = self.codigo
        self.comp['produtividade'] = self.obj_comp.produtividade
        self.comp['unidade'] = self.obj_comp.unidade

        self.comp['fic'] = self.get_fic()
        
        # EQUIPAMENTOS
        self.comp['tab_equipamentos'] = self.get_tab_equipamentos()
        custo_equipamentos = self.total_custo_equipamentos(
            self.comp['tab_equipamentos']
            )
        self.comp['custototalequipamentos']  = custo_equipamentos

        # MAO DE OBRA
        self.comp['tab_mao_de_obra'] = self.get_tab_mao_de_obra()
        custo_mao_de_obra = self.total_custo_mao_de_obra(
            self.comp['tab_mao_de_obra']
            )
        self.comp['custototalmaodeobra'] = custo_mao_de_obra

        # MATERIAIS
        self.comp['tab_material'] = self.get_tab_materiais()
        custo_materiais = self.total_custo_materiais(
            self.comp['tab_material']
            )
        self.comp['custototalmateriais'] = custo_materiais

        # ATIVIDADES AUXILIARES
        self.comp['tab_ativ_auxiliares'] = self.get_tab_ativ_auxiliares()
        custo_ativ_auxiliares = self.total_custo_ativ_auxiliares(
            self.comp['tab_ativ_auxiliares']
            )
        self.comp['custoativauxiliares'] = custo_ativ_auxiliares

        # TEMPO-FIXO
        self.comp['tempo_fixo'] = self.get_tab_tempo_fixo(
            self.codigo,
            self.comp['tab_material'],
            self.comp['tab_ativ_auxiliares']
            )
        self.comp['custotempofixo'] = self.total_custo_tempo_fixo(
            self.comp['tempo_fixo']
            )
        
        
        custoequipmobra = (
            self.comp['custototalequipamentos'] +
            self.comp['custototalmaodeobra']
        )
        self.comp['custoequipmobra'] = custoequipmobra
        custo_unit_exec = round(custoequipmobra / self.obj_comp.produtividade,
                                4)
        custo_fic = round(self.comp['fic'] * custo_unit_exec, 4)
        self.comp['custo_fic'] = custo_fic
        self.comp['custounitariodeexecucao'] = custo_unit_exec

        subtotal = (
            custo_unit_exec + self.comp['custototalmateriais'] +
            self.comp['custoativauxiliares'] + self.comp['custo_fic']
        )
        self.comp['subtotal'] = subtotal
        self.comp['custototal'] = round(subtotal + self.comp['custotempofixo'],
                                        2)

        return self.comp
    
    def get_fic(self):
        
        fic, created = CompFIC.objects.get_or_create(ano=self.ano, mes=self.mes,
                                                     estado=self.estado,
                                                     codigo=self.obj_comp,
                                                     defaults={'fic': 0})
        if created or fic.fic is None:
            return 0
        else:
            return fic.fic
        
    def get_tab_equipamentos(self):
        
        custos_equipamentos = EquipamentoCusto.objects.filter(
            ano=self.ano, mes=self.mes, estado=self.estado,
            desonerado=self.desonerado, codigo=OuterRef('codigo')
        ).values('custo_produtivo', 'custo_improdutivo')
        
        tab_equipamentos = EquipamentoRelacaoComp.objects.filter(
            comp=self.codigo
        ).select_related('codigo').annotate(
            custo_produtivo = Subquery(custos_equipamentos.values('custo_produtivo')[:1]),
            custo_improdutivo = Subquery(custos_equipamentos.values('custo_improdutivo')[:1]),
            custo_horario_total = Cast(
                F('quantidade') * (
                    F('utilizacao_operativa') * Subquery(custos_equipamentos.values('custo_produtivo')[:1]) +
                    F('utilizacao_improdutiva') * Subquery(custos_equipamentos.values('custo_improdutivo')[:1])
                ),
                DecimalField(max_digits=12, decimal_places=4)
            )
        )

        return tab_equipamentos
    
    def get_tab_mao_de_obra(self):

        custos_mao_de_obra = MaodeObraCusto.objects.filter(
            ano=self.ano, mes=self.mes, estado=self.estado, desonerado=self.desonerado,
            codigo=OuterRef('codigo')
        ).values('custo')
        maos_de_obra = MaodeObraRelacaoComp.objects.filter(
            comp=self.codigo
        ).select_related('codigo').annotate(
            preco=Subquery(custos_mao_de_obra[:1]),
            preco_total=Cast(F('quantidade') * Subquery(custos_mao_de_obra[:1]), 
                                DecimalField(max_digits=12, decimal_places=4)
                                )
            )
        
        return maos_de_obra
    
    def get_tab_materiais(self):
        custos_materiais = MaterialCusto.objects.filter(
            ano=self.ano, mes=self.mes, estado=self.estado, desonerado=self.desonerado,
            codigo=OuterRef('codigo')
        ).values('preco_unitario')
        materiais = MaterialRelacaoComp.objects.filter(
            comp=self.codigo
        ).select_related('codigo').annotate(
            preco=Subquery(custos_materiais[:1]),
            preco_total=Cast(F('quantidade') * Subquery(custos_materiais[:1]),
                                DecimalField(max_digits=12, decimal_places=4)
                                )
            )
        
        return materiais
    
    @staticmethod
    def total_custo_equipamentos(tab_equipamentos):
        custo_equipamentos = tab_equipamentos.aggregate(
            custo_total=Sum('custo_horario_total')
            )
        if not custo_equipamentos['custo_total']:
            custo_equipamentos['custo_total'] = 0

        return custo_equipamentos['custo_total']
    
    @staticmethod
    def total_custo_mao_de_obra(tab_mao_de_obra):
        
        custo_mao_de_obra = tab_mao_de_obra.aggregate(
            custo_total=Sum('preco_total')
            )
        if not custo_mao_de_obra['custo_total']:
            custo_mao_de_obra['custo_total'] = 0

        return custo_mao_de_obra['custo_total']
    
    @staticmethod
    def total_custo_materiais(tab_material):
        custo_materiais = tab_material.aggregate(
            custo_total=Sum('preco_total')
            )
        if not custo_materiais['custo_total']:
            custo_materiais['custo_total'] = 0
        
        return custo_materiais['custo_total']
    
    def get_tab_ativ_auxiliares(self):
        
        ativ_auxiliares = AtividadeAuxiliarRelacaoComp.objects.filter(codigo=self.codigo)
        if ativ_auxiliares:
            list_ativ_auxiliares = []
            for ativ_auxiliar in ativ_auxiliares:
                quantidade = ativ_auxiliar.quantidade
                ativ_aux_obj = Composicao(ativ_auxiliar.atividade_aux.codigo,
                                          self.estado, self.ano, self.mes,
                                          self.desonerado)
                list_ativ_auxiliares.append(ativ_aux_obj.get_comp_all_data(quantidade))
        else:
            return None
        
        return list_ativ_auxiliares
        
    @staticmethod
    def total_custo_ativ_auxiliares(tab_ativ_auxiliares):
        
        if tab_ativ_auxiliares:
            custoativauxiliares = 0
            for ativ_auxiliar in tab_ativ_auxiliares:
                custounitaux = round(ativ_auxiliar['quantidade'] * ativ_auxiliar['custototal'], 4)
                ativ_auxiliar['custounitaux'] = custounitaux
                custoativauxiliares += custounitaux
        else:
            custoativauxiliares = 0

        return custoativauxiliares
    
    def get_tab_tempo_fixo(self, codigo, tab_material, tab_ativ_auxiliares):

        tempo_fixo = []
        
        if tab_material:
            for material in tab_material:
                if material.tempo_fixo:
                    quantidade = material.quantidade_tempo_fixo
                    tempo_fixo_obj = Composicao(material.tempo_fixo.codigo,
                                                self.estado, self.ano, self.mes,
                                                self.desonerado)
                    tempo_fixo.append(tempo_fixo_obj.get_comp_all_data(quantidade, material.codigo))

        if tab_ativ_auxiliares:
            ativ_auxiliares = AtividadeAuxiliarRelacaoComp.objects.filter(codigo=codigo)
            for ativ_auxiliar in ativ_auxiliares:
                if ativ_auxiliar.tempo_fixo:
                    print(ativ_auxiliar.tempo_fixo)
                    quantidade = ativ_auxiliar.quantidade_tempo_fixo
                    tempo_fixo_obj = Composicao(ativ_auxiliar.tempo_fixo.codigo,
                                                self.estado, self.ano, self.mes,
                                                self.desonerado)
                    tempo_fixo.append(tempo_fixo_obj.get_comp_all_data(quantidade, ativ_auxiliar.codigo))
        
        if tempo_fixo == []:
            return None
        
        return tempo_fixo
    
    @staticmethod
    def total_custo_tempo_fixo(tab_tempo_fixo):
        if tab_tempo_fixo:
            custo_tempo_fixo = 0
            for tempo_fixo in tab_tempo_fixo:
                custo_unit_tempofixo = round(tempo_fixo['quantidade'] * tempo_fixo['custototal'],4)
                tempo_fixo['custounittempofixo'] = custo_unit_tempofixo
                custo_tempo_fixo += custo_unit_tempofixo
        else:
            custo_tempo_fixo = 0

        return custo_tempo_fixo