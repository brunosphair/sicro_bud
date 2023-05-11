from django.views.generic import TemplateView
from .models import (
    Sicro, MaodeObraRelacaoComp, MaodeObraCusto,EquipamentoCusto,
    EquipamentoRelacaoComp, MaterialRelacaoComp, MaterialCusto,
    AtividadeAuxiliarRelacaoComp, CompFIC
)
from django.shortcuts import get_object_or_404
from django.db.models import Case, F, OuterRef, Subquery, DecimalField, Sum, Value, When
from django.db.models.functions import Cast
from django.core.cache import cache
import concurrent.futures
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
    
class TesteView(TemplateView):
    template_name = "lista_composicoes.html"

    def get_context_data(self, **kwargs):

        time_start = time.time()
        context = super().get_context_data(**kwargs)
        estado = "PR"
        ano = 2022
        mes = 1
        desonerado = "N"

        # comp_list = ['5909007']
        # comp_list = ['0307732','0308308','0308313','0308309','0308310','0308311','0308312','0308307','0308322','0308327','0308323','0308324','0308325','0308326','0308321','0308315','0308320','0308316','0308317','0308318','0308319','0308314','0308250','0308251','0308268','0308252','0308253','0308254','0308255','0308256','0308257','0308258','0308259','0308260','0308261','0308262','0308263','0308264','0308265','0308266','0308267','0308288','0308289','0308306','0308290','0308291','0308292','0308293','0308294','0308295','0308296','0308297','0308298','0308299','0308300','0308301','0308302','0308303','0308304','0308305','0308269','0308270','0308287','0308271','0308272','0308273','0308274','0308275','0308276','0308277','0308278','0308279','0308280','0308281','0308282','0308283','0308284','0308285','0308286','0307733','0307734','0307735','0307736','0307737','0307730','0307084','0407818','0407819','0407820','0407740','0408037','0408038','0408039','0408041','0408042','0408031','0408032','0408033','0408035','0408036','0408067','0407743','0605706','0607137','0606785','0607139','0606787','0607140','0606788','0607141','0606789','0607144','0606792','0607142','0606790','0607145','0606793','0607146','0606794','0607143','0606791','0607147','0606795','0607112','0606760','0607113','0606761','0606762','0607114','0607116','0606764','0607115','0606763','0607117','0606765','0607118','0606766','0607120','0606768','0607119','0606767','0607121','0606769','0607123','0606771','0607122','0606770','0607125','0606773','0607124','0606772','0607126','0606774','0607127','0606775','0607129','0606777','0607128','0606776','0607130','0606778','0607131','0606779','0607133','0606781','0607132','0606780','0607134','0606782','0607136','0606784','0607135','0606783','0607138','0606786','0606842','0606832','0606843','0606833','0606845','0606835','0606844','0606834','0606847','0606837','0606846','0606836','0606848','0606838','0606849','0606839','0606850','0606840','0606851','0606841','0605604','0605695','0605607','0605696','0605608']
        list_comp = list(Sicro.objects.values('codigo'))
        # print(list_comp)
        comp_list = []
        for codigo in list_comp:
            comp_list.append(codigo['codigo'])
        # comp_list = ['0307730']
        # equip_info = EquipamentoCusto.objects.filter(
        #         ano=2022, mes=1, estado="PR", desonerado="N"
        #     ).values_list('codigo__codigo', 'custo_produtivo', 'custo_improdutivo')
        lista_precos = test_composicoes(comp_list, estado, ano, mes, desonerado)
        
        context['lista_precos'] = lista_precos
        time_end = time.time()
        # print('tempo decorrido: ', time_end - time_start, ' segundos')

        return context
    
def get_composition_cost(comp, equip_info):
    comp = Composicao(comp, "PR", 2022, 1, "N")
    custo = comp.get_custo_total(equip_info=equip_info)
    return custo
    
def test_composicoes(comp_list, estado, ano, mes, desonerado):

    fic_info = list(get_fic_info(estado, ano, mes).values())
    # print(fic_info)

    dict_fic_info = {}
    for dicionario in fic_info:
        codigo = dicionario['codigo_id']
        fic = dicionario['fic']
        dict_fic_info[codigo] = fic

    # ATIVIDADES AUXILIARES

    # Pega atividades auxiliares e respectivas quantidades
    codigos_formatados = ', '.join([f"'{codigo}'" for codigo in comp_list])
    query = f'''
    WITH RECURSIVE todas_comp(id, codigo_id, atividade_aux_id, quantidade, tempo_fixo_id, quantidade_tempo_fixo, nivel) AS (
        SELECT id, codigo_id, atividade_aux_id, quantidade, tempo_fixo_id, quantidade_tempo_fixo, 1 as nivel
        FROM composicoes_atividadeauxiliarrelacaocomp
        WHERE codigo_id IN ({codigos_formatados})
    UNION ALL
        SELECT cp.id, cp.codigo_id, cp.atividade_aux_id, cp.quantidade, cp.tempo_fixo_id, cp.quantidade_tempo_fixo, tc.nivel + 1 as nivel
        FROM composicoes_atividadeauxiliarrelacaocomp AS cp, todas_comp AS tc
        WHERE cp.codigo_id = tc.atividade_aux_id
    )
    SELECT * FROM todas_comp;
    '''
    comp_nivel = {}
    # Transforma isso em um dicionário
    ativ_auxiliares = AtividadeAuxiliarRelacaoComp.objects.raw(query)
    list_ativ_auxiliares = set([ativ_auxiliar.atividade_aux_id for ativ_auxiliar in ativ_auxiliares])
    print(list_ativ_auxiliares)
    dict_ativ_auxiliares = {}
    print(ativ_auxiliares)
    for ativ_auxiliar in ativ_auxiliares:
        comp = ativ_auxiliar.codigo_id
        ativ_aux = ativ_auxiliar.atividade_aux_id
        quantidade = ativ_auxiliar.quantidade
        nivel = ativ_auxiliar.nivel
        if comp in dict_ativ_auxiliares:
            if not [ativ_aux, quantidade] in dict_ativ_auxiliares[comp]:
                dict_ativ_auxiliares[comp].append([ativ_aux, quantidade])
        else:
            dict_ativ_auxiliares[comp] = [[ativ_aux, quantidade]]
        if ativ_aux in comp_nivel:
            if comp_nivel[ativ_aux] < nivel:
                comp_nivel[ativ_aux] = nivel
        else:
            comp_nivel[ativ_aux] = nivel
    
    # print('comp_nivel:', comp_nivel)

    # primeira chave do dicionário e a atividade principal, o conteúdo é uma lista de tuplas
    # onde o primeiro item é o código e o segundo é a quantidade da composição
    # print(dict_ativ_auxiliares)

    # print(list_ativ_auxiliares)

    # adiciona as atividades auxiliares à list_comp
    in_ativ_aux_but_not_in_comp_list = list_ativ_auxiliares - set(comp_list)
    list_total = comp_list + list(in_ativ_aux_but_not_in_comp_list)

    materiais_tempo_fixo = list(MaterialRelacaoComp.objects.exclude(tempo_fixo_id=None).filter(
        comp__in=list_total
        ).values('comp_id', 'tempo_fixo_id', 'quantidade_tempo_fixo'))

    ativ_aux_tempo_fixo = list(AtividadeAuxiliarRelacaoComp.objects.exclude(tempo_fixo_id=None).filter(
        codigo__in=list_total
        ).values('codigo_id', 'tempo_fixo_id', 'quantidade_tempo_fixo'))

    # print(ativ_aux_tempo_fixo)
    
    dict_tempo_fixo = {}
    list_tempo_fixo = set()
    for dicionario in materiais_tempo_fixo:
        comp_id = dicionario['comp_id']
        tempo_fixo_id = dicionario['tempo_fixo_id']
        qtde_tempo_fixo = dicionario['quantidade_tempo_fixo']
        dict_tempo_fixo.setdefault(comp_id, []).append([tempo_fixo_id, qtde_tempo_fixo])
        list_tempo_fixo.add(tempo_fixo_id)
    for dicionario in ativ_aux_tempo_fixo:
        comp_id = dicionario['codigo_id']
        tempo_fixo_id = dicionario['tempo_fixo_id']
        qtde_tempo_fixo = dicionario['quantidade_tempo_fixo']
        list_tempo_fixo.add(tempo_fixo_id)
        dict_tempo_fixo.setdefault(comp_id, []).append([tempo_fixo_id, qtde_tempo_fixo])
    # print(dict_tempo_fixo)
    # print('lista tempo fixo:', list_tempo_fixo)

    in_tempo_fixo_but_not_list_total = list_tempo_fixo - set(list_total)
    list_total = list_total + list(in_tempo_fixo_but_not_list_total)

    for item in list_total:
        # print(item)
        if item not in comp_nivel:
            comp_nivel[item] = 0
            # print(item)
    maior_nivel = max(comp_nivel.values())

    composicoes = Sicro.objects.filter(pk__in=list_total)
    composicoes_list = list(composicoes.values())

    equipamentos = list(EquipamentoRelacaoComp.objects.filter(comp__in=composicoes).annotate(
        custo_produtivo=F('codigo__equipamentocusto__custo_produtivo'),
        custo_improdutivo=F('codigo__equipamentocusto__custo_improdutivo'),
        custo_horario_total=Cast(
                F('quantidade') * (
                    F('utilizacao_operativa') * F('custo_produtivo') +
                    F('utilizacao_improdutiva') * F('custo_improdutivo')
                ),
                DecimalField(max_digits=12, decimal_places=4)
            )
    ).values('comp').annotate(total=Sum('custo_horario_total')))


    mao_de_obra = list(MaodeObraRelacaoComp.objects.filter(comp__in=composicoes).annotate(
        custo=F('codigo__maodeobracusto__custo'),
        preco_total=Cast(F('quantidade') * F('custo'), 
                                DecimalField(max_digits=12, decimal_places=4)
                                )
    ).values('comp').annotate(total=Sum('preco_total')))
    
    # print(equipamentos)
    
    soma = {}

    for dicionario in equipamentos:
        comp = dicionario['comp']
        total = dicionario['total']
        soma[comp] = soma.get(comp, 0) + total

    for dicionario in mao_de_obra:
        comp = dicionario['comp']
        total = dicionario['total']
        soma[comp] = soma.get(comp, 0) + total

    for comp_code in list_total:
        if comp_code not in soma:
            soma[comp_code] = 0
    
    print('soma:', soma['0605460'])
    # print(custo_mao_de_obra)
    # print(soma.keys())

    dict_prod = {}
    dict_descricao = {}

    for dicionario in composicoes_list:
        codigo = dicionario['codigo']
        prod = dicionario['produtividade']
        descricao = dicionario['descricao']
        dict_prod[codigo] = prod
        dict_descricao[codigo] = descricao
    # print(dict_prod.keys())

    dict_custo_unit = {}
    for key in soma.keys():
        custo_unit = soma[key] / dict_prod[key]
        dict_custo_unit[key] = round(custo_unit,4)

    print('custo_unit:', dict_custo_unit['0605460'])

    dict_custo_unit_com_fic = {}
    
    for key in dict_custo_unit.keys():
        if key in dict_fic_info.keys():
            if dict_fic_info[key]:
                fic = dict_fic_info[key]
                dict_custo_unit_com_fic[key] = dict_custo_unit[key] + round(dict_custo_unit[key] * fic, 4)
            else:
                dict_custo_unit_com_fic[key] = dict_custo_unit[key]
        else:
            dict_custo_unit_com_fic[key] = dict_custo_unit[key]

    print(dict_custo_unit_com_fic['0605460'])


    materiais = list(MaterialRelacaoComp.objects.filter(comp__in=composicoes).annotate(
        preco_unitario=F('codigo__materialcusto__preco_unitario'),
        preco_total=Cast(F('quantidade') * F('preco_unitario'), 
                                DecimalField(max_digits=12, decimal_places=4)
                                )
    ).values('comp').annotate(total=Sum('preco_total')))

    dict_materiais = {}
    for dicionario in materiais:
        comp = dicionario['comp']
        total = dicionario['total']
        dict_materiais[comp] = total

    dict_custo_unit_e_material = {}

    for key in dict_custo_unit_com_fic:
        soma = dict_custo_unit_com_fic[key] + dict_materiais.get(key, 0)
        dict_custo_unit_e_material[key] = soma
    
    print('com material:', dict_custo_unit_e_material['0605460'])

    dict_custo_com_tempo_fixo = {}
    for key in dict_custo_unit_e_material:
        if dict_tempo_fixo.get(key, 0) == 0:
            dict_custo_com_tempo_fixo[key] = dict_custo_unit_e_material[key]
        else:
            total_ativ_auxiliares = 0
            for item in dict_tempo_fixo[key]:
                quantidade = item[1]
                tempo_fixo_id = item[0]
                preco_tempo_fixo = dict_custo_unit_e_material[tempo_fixo_id]
                # print('quantidade:', quantidade, 'preco:', preco_tempo_fixo)
                total_ativ_auxiliares += round(quantidade * round(preco_tempo_fixo, 2), 4)
            # print('id:', key, 'total_tempo_fixo:', total_ativ_auxiliares)
            dict_custo_com_tempo_fixo[key] = dict_custo_unit_e_material[key] + total_ativ_auxiliares

    print(dict_custo_com_tempo_fixo['0605460'])
    # print(list_total)

    dict_custo_total = {}

    # print('dict_ativ_aux:', dict_ativ_auxiliares)
    # print('ativ_aux:', dict_ativ_auxiliares)
    for nivel in reversed(range(maior_nivel + 1)):
        # print(nivel)
        for comp_code in list_total:
            if comp_nivel[comp_code] == nivel:
                total_ativ_auxiliar = 0
                if dict_ativ_auxiliares.get(comp_code, 0) == 0:
                    dict_custo_total[comp_code] = round(dict_custo_com_tempo_fixo[comp_code], 2)
                else:
                    total_ativ_auxiliar = 0
                    if comp_code == '2003849':
                        print(dict_ativ_auxiliares[comp_code])
                    for item in dict_ativ_auxiliares[comp_code]:
                        quantidade = item[1]
                        preco = dict_custo_total[item[0]]
                        # multiplicacao =  round(quantidade * preco, 4)
                        # print('comp:', key, 'ativ_aux:', item[0], 'total:', multiplicacao)
                        total_ativ_auxiliar += round(quantidade * preco, 4)
                        if comp_code == '2003849':
                            print(item, total_ativ_auxiliar)
                    dict_custo_total[comp_code] = round(dict_custo_com_tempo_fixo[comp_code] + total_ativ_auxiliar, 2)

    print(dict_custo_total['0605460'])
    lista_final = []
    for item in comp_list:
        comp_code = item
        descricao = dict_descricao[comp_code]
        custo = dict_custo_total[comp_code]
        lista_final.append((comp_code, descricao, custo))
    
    # print(lista_final)
    
    return lista_final
    # for key in dict_custo_com_tempo_fixo.keys():
        # print(dict_ativ_auxiliares.get(key, 0))
        
        # if dict_ativ_auxiliares.get(key, 0) == 0:
        #     dict_custo_total[key] = round(dict_custo_com_tempo_fixo[key], 2)
        # else:
        #     total_ativ_auxiliar = 0
        #     for item in dict_ativ_auxiliares[key]:
        #         quantidade = item[1]
        #         preco = dict_custo_com_tempo_fixo[item[0]]
        #         multiplicacao =  round(quantidade * round(preco, 2), 4)
        #         # print('comp:', key, 'ativ_aux:', item[0], 'total:', multiplicacao)
        #         total_ativ_auxiliar += round(quantidade * round(preco, 2), 4)
        #     # print('comp:', key, 'ativ_aux:', total_ativ_auxiliar)
        #     dict_custo_total[key] = dict_custo_com_tempo_fixo[key] + total_ativ_auxiliar
    
    # print(dict_custo_total)
    # print(dict_custo_unit_e_material)

    # equip_e_mao_de_obra = equipamentos.union(mao_de_obra).values('comp_id')
    # print(equip_e_mao_de_obra.query)


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
        self.comp['custototalequipamentos']  = custo_equipamentos
        

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

        custos_dict = {codigo: (custo, custo_improdutivo) for codigo, custo, custo_improdutivo in equip_info if codigo in codigos}

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
                                DecimalField(max_digits=12, decimal_places=4)
                                )
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
            *[When(codigo__codigo=codigo, then=(Value(preco_unitario))) for codigo, preco_unitario in custos_dict.items()],
            default=0,
            output_field=DecimalField(max_digits=12, decimal_places=4)
            ),
            preco_total=Cast(F('quantidade') * F('preco'), 
                                DecimalField(max_digits=12, decimal_places=4)
                                )
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
                custo_unit_tempofixo = round(tempo_fixo['quantidade'] * tempo_fixo['custototal'],4)
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