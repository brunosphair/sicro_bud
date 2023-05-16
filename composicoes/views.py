from django.views.generic import TemplateView
from .models import (
    Sicro, MaodeObraRelacaoComp, MaodeObraCusto, EquipamentoCusto,
    EquipamentoRelacaoComp, MaterialRelacaoComp, MaterialCusto,
    AtividadeAuxiliarRelacaoComp, CompFIC, GrupoSicro
)
from django.shortcuts import get_object_or_404
from django.db.models import Case, F, OuterRef, Subquery, DecimalField, Sum, Value, When
from django.db.models.functions import Cast
from django.core.cache import cache
import time


class CompView(TemplateView):
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
        start_time = time.time()
        comp_data = comp.get_comp_all_data()

        context['comp'] = comp_data
        end_time = time.time()
        print('tempo decorrido: ', end_time - start_time, ' segundos')

        return context


class CompTodasView(TemplateView):
    template_name = "lista_composicoes.html"

    def get_context_data(self, **kwargs):

        time_start = time.time()
        context = super().get_context_data(**kwargs)
        estado = kwargs.get('estado')
        ano = kwargs.get('ano')
        mes = kwargs.get('mes')
        desonerado = kwargs.get('des')

        comp_list_dict = list(Sicro.objects.values('codigo'))
        print(comp_list_dict)

        lista_precos = test_composicoes(comp_list_dict, estado, ano, mes, desonerado)

        context['lista_precos'] = lista_precos
        time_end = time.time()
        print('tempo decorrido: ', time_end - time_start, ' segundos')

        return context


def test_composicoes(comp_list_dict, estado, ano, mes, desonerado):

    comp_list = []
    for codigo in comp_list_dict:
        comp_list.append(codigo['codigo'])
    fic_list_dict = list(get_fic_info(estado, ano, mes).values())

    fic_dict = {}
    for dicionario in fic_list_dict:
        codigo = dicionario['codigo_id']
        fic = dicionario['fic']
        fic_dict[codigo] = fic

    # ATIVIDADES AUXILIARES

    # Pega atividades auxiliares e respectivas quantidades
    codigos_formatados = ', '.join([f"'{codigo}'" for codigo in comp_list])
    query = f'''
    WITH RECURSIVE todas_comp(id, codigo_id, atividade_aux_id, quantidade, tempo_fixo_id, quantidade_tempo_fixo,
        nivel) AS (
            SELECT id, codigo_id, atividade_aux_id, quantidade, tempo_fixo_id, quantidade_tempo_fixo, 1 as nivel
            FROM composicoes_atividadeauxiliarrelacaocomp
            WHERE codigo_id IN ({codigos_formatados})
        UNION ALL
            SELECT cp.id, cp.codigo_id, cp.atividade_aux_id, cp.quantidade, cp.tempo_fixo_id, cp.quantidade_tempo_fixo,
                tc.nivel + 1 AS nivel
                    FROM composicoes_atividadeauxiliarrelacaocomp AS cp, todas_comp AS tc
                    WHERE cp.codigo_id = tc.atividade_aux_id
        )
    SELECT * FROM todas_comp;
    '''
    comp_nivel = {}
    # Transforma isso em um dicionário
    ativ_auxiliares_raw = AtividadeAuxiliarRelacaoComp.objects.raw(query)
    ativ_auxiliares_set = set([ativ_auxiliar.atividade_aux_id for ativ_auxiliar in ativ_auxiliares_raw])
    ativ_auxiliares_dict = {}
    for ativ_auxiliar in ativ_auxiliares_raw:
        comp = ativ_auxiliar.codigo_id
        ativ_aux = ativ_auxiliar.atividade_aux_id
        quantidade = ativ_auxiliar.quantidade
        nivel = ativ_auxiliar.nivel
        if comp in ativ_auxiliares_dict:
            if not [ativ_aux, quantidade] in ativ_auxiliares_dict[comp]:
                ativ_auxiliares_dict[comp].append([ativ_aux, quantidade])
        else:
            ativ_auxiliares_dict[comp] = [[ativ_aux, quantidade]]
        if ativ_aux in comp_nivel:
            if comp_nivel[ativ_aux] < nivel:
                comp_nivel[ativ_aux] = nivel
        else:
            comp_nivel[ativ_aux] = nivel

    # a chave do dicionário é a atividade principal, o conteúdo é uma lista de
    # tuplas onde o primeiro item é o código e o segundo é a quantidade da
    # composição

    # adiciona as atividades auxiliares à list_comp
    in_ativ_aux_but_not_in_comp_list = ativ_auxiliares_set - set(comp_list)
    list_total = comp_list + list(in_ativ_aux_but_not_in_comp_list)

    materiais_tempo_fixo = list(MaterialRelacaoComp.objects.exclude(tempo_fixo_id=None).filter(
        comp__in=list_total
        ).values('comp_id', 'tempo_fixo_id', 'quantidade_tempo_fixo'))

    ativ_aux_tempo_fixo = list(AtividadeAuxiliarRelacaoComp.objects.exclude(tempo_fixo_id=None).filter(
        codigo__in=list_total
        ).values('codigo_id', 'tempo_fixo_id', 'quantidade_tempo_fixo'))

    tempo_fixo_dict = {}
    tempo_fixo_set = set()
    for dicionario in materiais_tempo_fixo:
        comp_id = dicionario['comp_id']
        tempo_fixo_id = dicionario['tempo_fixo_id']
        qtde_tempo_fixo = dicionario['quantidade_tempo_fixo']
        tempo_fixo_dict.setdefault(comp_id, []).append([tempo_fixo_id, qtde_tempo_fixo])
        tempo_fixo_set.add(tempo_fixo_id)
    for dicionario in ativ_aux_tempo_fixo:
        comp_id = dicionario['codigo_id']
        tempo_fixo_id = dicionario['tempo_fixo_id']
        qtde_tempo_fixo = dicionario['quantidade_tempo_fixo']
        tempo_fixo_set.add(tempo_fixo_id)
        tempo_fixo_dict.setdefault(comp_id, []).append([tempo_fixo_id, qtde_tempo_fixo])

    in_tempo_fixo_but_not_list_total = tempo_fixo_set - set(list_total)
    list_total = list_total + list(in_tempo_fixo_but_not_list_total)

    for item in list_total:
        if item not in comp_nivel:
            comp_nivel[item] = 0
    maior_nivel = max(comp_nivel.values())

    composicoes = Sicro.objects.filter(pk__in=list_total)
    composicoes_list = list(composicoes.values())

    equipamentos_list_dict = get_equip_list_dict(list_total,
                                                 estado, ano, mes, desonerado)

    mobra_list_dict = get_mobra_list_dict(list_total,
                                          estado, ano, mes, desonerado)

    soma = {}

    for dicionario in equipamentos_list_dict:
        comp = dicionario['comp']
        total = dicionario['total']
        soma[comp] = soma.get(comp, 0) + total

    for dicionario in mobra_list_dict:
        comp = dicionario['comp']
        total = dicionario['total']
        soma[comp] = soma.get(comp, 0) + total

    for comp_code in list_total:
        if comp_code not in soma:
            soma[comp_code] = 0

    prod_dict = {}
    descricao_dict = {}

    for dicionario in composicoes_list:
        codigo = dicionario['codigo']
        prod = dicionario['produtividade']
        descricao = dicionario['descricao']
        prod_dict[codigo] = prod
        descricao_dict[codigo] = descricao

    custo_unit_dict = {}
    for key in soma.keys():
        custo_unit = soma[key] / prod_dict[key]
        custo_unit_dict[key] = round(custo_unit, 4)

    dict_custo_unit_com_fic = {}

    for key in custo_unit_dict.keys():
        if key in fic_dict.keys():
            if fic_dict[key]:
                fic = fic_dict[key]
                dict_custo_unit_com_fic[key] = custo_unit_dict[key] + round(custo_unit_dict[key] * fic, 4)
            else:
                dict_custo_unit_com_fic[key] = custo_unit_dict[key]
        else:
            dict_custo_unit_com_fic[key] = custo_unit_dict[key]

    materiais_list_dict = get_materiais_list_dict(list_total, estado,
                                                  ano, mes, desonerado)

    dict_materiais = {}
    for dicionario in materiais_list_dict:
        comp = dicionario['comp']
        total = dicionario['total']
        dict_materiais[comp] = total

    dict_custo_unit_e_material = {}

    for key in dict_custo_unit_com_fic:
        soma = dict_custo_unit_com_fic[key] + dict_materiais.get(key, 0)
        dict_custo_unit_e_material[key] = soma

    dict_custo_com_tempo_fixo = {}
    for key in dict_custo_unit_e_material:
        if tempo_fixo_dict.get(key, 0) == 0:
            dict_custo_com_tempo_fixo[key] = dict_custo_unit_e_material[key]
        else:
            total_ativ_auxiliares = 0
            for item in tempo_fixo_dict[key]:
                quantidade = item[1]
                tempo_fixo_id = item[0]
                preco_tempo_fixo = dict_custo_unit_e_material[tempo_fixo_id]
                total_ativ_auxiliares += round(quantidade * round(preco_tempo_fixo, 2), 4)
            dict_custo_com_tempo_fixo[key] = dict_custo_unit_e_material[key] + total_ativ_auxiliares

    dict_custo_total = {}

    for nivel in reversed(range(maior_nivel + 1)):
        for comp_code in list_total:
            if comp_nivel[comp_code] == nivel:
                total_ativ_auxiliar = 0
                if ativ_auxiliares_dict.get(comp_code, 0) == 0:
                    dict_custo_total[comp_code] = round(dict_custo_com_tempo_fixo[comp_code], 2)
                else:
                    total_ativ_auxiliar = 0
                    for item in ativ_auxiliares_dict[comp_code]:
                        quantidade = item[1]
                        preco = dict_custo_total[item[0]]
                        total_ativ_auxiliar += round(quantidade * preco, 4)
                    dict_custo_total[comp_code] = round(dict_custo_com_tempo_fixo[comp_code] + total_ativ_auxiliar, 2)

    grupos_list = list(GrupoSicro.objects.values())
    grupos_dict = {}
    for item in grupos_list:
        codigo = item['grupo']
        descricao = item['descricao']
        grupos_dict[codigo] = descricao

    for item in comp_list_dict:
        comp_code = item['codigo']
        item['descricao'] = descricao_dict[comp_code]
        item['custo'] = dict_custo_total[comp_code]
        item['grupo'] = grupos_dict[comp_code[0:2]].upper()

    return comp_list_dict


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

        equip_info = get_equip_info(self.estado, self.ano, self.mes,
                                    self.desonerado)
        mao_de_obra_info = get_mao_de_obra_info(self.estado, self.ano, self.mes,
                                                self.desonerado)
        material_info = get_material_info(self.estado, self.ano, self.mes,
                                          self.desonerado)

        # Definicoes gerais da composicao
        self.comp['descricao'] = self.obj_comp.descricao
        self.comp['codigo'] = self.codigo
        self.comp['produtividade'] = self.obj_comp.produtividade
        self.comp['unidade'] = self.obj_comp.unidade

        self.comp['fic'] = self.get_fic()

        # EQUIPAMENTOS

        self.comp['tab_equipamentos'] = self.get_tab_equipamentos(equip_info)
        custo_equipamentos = self.total_custo_equipamentos(
            self.comp['tab_equipamentos']
            )
        self.comp['custototalequipamentos'] = custo_equipamentos

        # MAO DE OBRA
        self.comp['tab_mao_de_obra'] = self.get_tab_mao_de_obra(mao_de_obra_info)
        custo_mao_de_obra = self.total_custo_mao_de_obra(
            self.comp['tab_mao_de_obra']
            )
        self.comp['custototalmaodeobra'] = custo_mao_de_obra

        # MATERIAIS
        self.comp['tab_material'] = self.get_tab_materiais(material_info)
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
            self.comp['tab_ativ_auxiliares'],
            equip_info=equip_info,
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

    def get_tab_equipamentos(self, equip_info):

        codigos = list(EquipamentoRelacaoComp.objects.filter(comp=self.codigo).values_list('codigo', flat=True))

        custos_dict = {codigo: (custo, custo_improdutivo) for codigo,
                       custo, custo_improdutivo in equip_info if codigo in codigos}

        tab_equipamentos = EquipamentoRelacaoComp.objects.filter(
            comp=self.codigo, codigo__in=custos_dict.keys()
        ).select_related('codigo').annotate(
            custo_produtivo=Case(
                *[When(codigo__codigo=codigo, then=Value(custo[0])) for codigo, custo in custos_dict.items()],
                default=0,
                output_field=DecimalField(max_digits=12, decimal_places=4)
            ),
            custo_improdutivo=Case(
                *[When(codigo__codigo=codigo, then=Value(custo[1])) for codigo, custo in custos_dict.items()],
                default=0,
                output_field=DecimalField(max_digits=12, decimal_places=4)
            ),
            custo_horario_total=Cast(
                F('quantidade') * (
                    F('utilizacao_operativa') * F('custo_produtivo') +
                    F('utilizacao_improdutiva') * F('custo_improdutivo')
                ),
                DecimalField(max_digits=12, decimal_places=4)
            )
        )

        tab_equipamentos_list = list(tab_equipamentos)
        # print('lista:', tab_equipamentos_list)

        return tab_equipamentos_list

    def get_tab_mao_de_obra(self, mao_de_obra_info):

        codigos = MaodeObraRelacaoComp.objects.filter(comp=self.codigo).values_list('codigo', flat=True)

        # mao_de_obra_info = MaodeObraCusto.objects.filter(
        #         ano=self.ano, mes=self.mes, estado=self.estado, desonerado=self.desonerado
        #     ).values_list('codigo__codigo', 'custo')

        custos_dict = {codigo: custo for codigo, custo in mao_de_obra_info if codigo in codigos}

        tab_mao_de_obra = MaodeObraRelacaoComp.objects.filter(
            comp=self.codigo, codigo__in=custos_dict.keys()
        ).select_related('codigo').annotate(
            preco=Case(
                *[When(codigo__codigo=codigo, then=(Value(custo))) for codigo, custo in custos_dict.items()],
                default=0,
                output_field=DecimalField(max_digits=12, decimal_places=4)
            ),
            preco_total=Cast(F('quantidade') * F('preco'),
                             DecimalField(max_digits=12, decimal_places=4))
            )

        # print(tab_mao_de_obra.query)

        tab_mao_de_obra_list = list(tab_mao_de_obra)

        return tab_mao_de_obra_list

    def get_tab_materiais(self, material_info):

        codigos = MaterialRelacaoComp.objects.filter(comp=self.codigo).values_list('codigo', flat=True)

        # material_info = MaterialCusto.objects.filter(
        #         ano=self.ano, mes=self.mes, estado=self.estado, desonerado=self.desonerado
        #     ).values_list('codigo__codigo', 'preco_unitario')

        custos_dict = {codigo: preco_unitario for codigo, preco_unitario in material_info if codigo in codigos}

        tab_materiais = MaterialRelacaoComp.objects.filter(
            comp=self.codigo, codigo__in=custos_dict.keys()
        ).select_related('codigo').annotate(
            preco=Case(
                *[When(codigo__codigo=codigo,
                       then=(Value(preco_unitario))) for codigo, preco_unitario in custos_dict.items()],
                default=0,
                output_field=DecimalField(max_digits=12, decimal_places=4)
            ),
            preco_total=Cast(F('quantidade') * F('preco'),
                             DecimalField(max_digits=12, decimal_places=4))
            )

        tab_materiais_list = list(tab_materiais)

        return tab_materiais_list

    @staticmethod
    def total_custo_equipamentos(tab_equipamentos):

        custo_equipamentos = sum(obj.custo_horario_total for obj in tab_equipamentos)

        return custo_equipamentos

    @staticmethod
    def total_custo_mao_de_obra(tab_mao_de_obra):

        custo_mao_de_obra = sum(obj.preco_total for obj in tab_mao_de_obra)

        return custo_mao_de_obra

    @staticmethod
    def total_custo_materiais(tab_material):
        custo_materiais = sum(obj.preco_total for obj in tab_material)

        return custo_materiais

    def get_custo_total(self, equip_info):
        all_data = self.get_comp_all_data()

        custo_total = all_data['custototal']

        return custo_total

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

    def get_tab_tempo_fixo(self, codigo, tab_material, tab_ativ_auxiliares, equip_info):

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
                custo_unit_tempofixo = round(tempo_fixo['quantidade'] * tempo_fixo['custototal'], 4)
                tempo_fixo['custounittempofixo'] = custo_unit_tempofixo
                custo_tempo_fixo += custo_unit_tempofixo
        else:
            custo_tempo_fixo = 0

        return custo_tempo_fixo


def get_equip_info(estado, ano, mes, desonerado):

    equip_info_str = 'equip_info_' + estado + '_' + str(ano) + '_' + str(mes) + '_' + desonerado
    equip_info = cache.get(equip_info_str)
    if equip_info is None:
        equip_info = EquipamentoCusto.objects.filter(
            ano=ano, mes=mes, estado=estado, desonerado=desonerado
        ).values_list('codigo__codigo', 'custo_produtivo', 'custo_improdutivo')
        cache.set(equip_info_str, equip_info, 60 * 10)

    return equip_info


def get_mao_de_obra_info(estado, ano, mes, desonerado):
    mao_de_obra_info_str = 'mao_de_obra_info_' + estado + '_' + str(ano) + '_' + str(mes) + '_' + desonerado
    mao_de_obra_info = cache.get(mao_de_obra_info_str)
    if mao_de_obra_info is None:
        mao_de_obra_info = MaodeObraCusto.objects.filter(
                ano=ano, mes=mes, estado=estado, desonerado=desonerado
            ).values_list('codigo__codigo', 'custo')
        cache.set(mao_de_obra_info_str, mao_de_obra_info)

    return mao_de_obra_info


def get_material_info(estado, ano, mes, desonerado):
    material_info_str = 'material_info_' + estado + '_' + str(ano) + '_' + str(mes) + '_' + desonerado
    material_info = cache.get(material_info_str)
    if material_info is None:
        material_info = MaterialCusto.objects.filter(
                ano=ano, mes=mes, estado=estado, desonerado=desonerado
            ).values_list('codigo__codigo', 'preco_unitario')

    return material_info


def get_fic_info(estado_str, ano_str, mes_str):
    fic_info = CompFIC.objects.filter(
        ano=ano_str, mes=mes_str, estado=estado_str
    )

    return fic_info


def get_equip_list_dict(comp_list, estado, ano, mes, desonerado):
    equip_list_dict = list(EquipamentoRelacaoComp.objects.filter(
            comp__in=comp_list
        ).annotate(
            custo_produtivo=Subquery(EquipamentoCusto.objects.filter(
                codigo=OuterRef('codigo_id'),
                estado=estado, ano=ano, mes=mes, desonerado=desonerado
            ).values('custo_produtivo')[:1]),
            custo_improdutivo=Subquery(EquipamentoCusto.objects.filter(
                codigo=OuterRef('codigo_id'),
                estado=estado, ano=ano, mes=mes, desonerado=desonerado
            ).values('custo_improdutivo')[:1]),
            custo_horario_total=Cast(
                    F('quantidade') * (
                        F('utilizacao_operativa') * F('custo_produtivo') +
                        F('utilizacao_improdutiva') * F('custo_improdutivo')
                    ),
                    DecimalField(max_digits=12, decimal_places=4)
                )
        ).values('comp').annotate(total=Sum('custo_horario_total')))

    return equip_list_dict


def get_mobra_list_dict(comp_list, estado, ano, mes, desonerado):
    mao_de_obra_list_dict = list(MaodeObraRelacaoComp.objects.filter(
        comp__in=comp_list).annotate(
            custo=Subquery(MaodeObraCusto.objects.filter(
                codigo=OuterRef('codigo'), estado=estado, ano=ano, mes=mes,
                desonerado=desonerado
            ).values('custo')[:1]),
            preco_total=Cast(F('quantidade') * F('custo'),
                             DecimalField(max_digits=12, decimal_places=4))
        ).values('comp').annotate(total=Sum('preco_total')))

    return mao_de_obra_list_dict


def get_materiais_list_dict(comp_list,
                            estado: str, ano: int, mes: int, desonerado: str):
    '''
    A partir dos dados de entrada, obtém uma lista de dicionários com as chaves
    'comp' e 'total', onde 'comp' é o codigo da composição e total é a soma dos
    valores dos materiais que a compõe.
    '''
    materiais_list_dict = list(MaterialRelacaoComp.objects.filter(
        comp__in=comp_list).annotate(
            preco_unitario=Subquery(MaterialCusto.objects.filter(
                codigo=OuterRef('codigo'), estado=estado, ano=ano, mes=mes,
                desonerado=desonerado
            ).values('preco_unitario')[:1]),
            preco_total=Cast(F('quantidade') * F('preco_unitario'),
                             DecimalField(max_digits=12, decimal_places=4))
        ).values('comp').annotate(total=Sum('preco_total')))

    return materiais_list_dict
