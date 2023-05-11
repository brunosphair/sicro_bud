from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here.
    
class Sicro(models.Model):
    codigo = models.CharField(max_length=7, primary_key=True, verbose_name="Código")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    produtividade = models.DecimalField(max_digits=20, decimal_places=4)
    unidade = models.CharField(max_length=10)

    def __str__(self):
        return self.descricao
    
    class Meta:
        indexes = [models.Index(fields=['codigo',]),]

class CompFIC(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=2)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(12)])
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2020),
                                                  MaxValueValidator(2023)])
    codigo = models.ForeignKey(Sicro, on_delete=models.CASCADE, verbose_name="Código")
    fic = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)

class MaodeObraDescricao(models.Model):
    codigo = models.CharField(max_length=5, verbose_name="Código", primary_key=True)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    unidade = models.CharField(max_length=10)

class MaodeObraCusto(models.Model):
    estado = models.CharField(max_length=2)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(12)])
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2020),
                                                  MaxValueValidator(2023)])
    desonerado = models.CharField(max_length=1)
    codigo = models.ForeignKey(MaodeObraDescricao, verbose_name="Código", on_delete=models.PROTECT)
    salario = models.DecimalField(max_digits=20, decimal_places=4, verbose_name="Salário")
    engargos_totais = models.DecimalField(max_digits=7, decimal_places=6)
    custo = models.DecimalField(max_digits=20, decimal_places=4)
    periculosidade_insalubridade = models.DecimalField(max_digits=7, decimal_places=6, verbose_name="Periculosidade/Insalubridade")

    class Meta:
        unique_together = ('estado', 'mes', 'ano', 'desonerado', 'codigo',)

class MaodeObraRelacaoComp(models.Model):
    comp = models.ForeignKey(Sicro, on_delete=models.CASCADE)
    codigo = models.ForeignKey(MaodeObraDescricao, verbose_name="Código", on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=20, decimal_places=5)

    class Meta:
        unique_together = ('comp', 'codigo',)
        indexes = [models.Index(fields=['comp', 'codigo',]),]

class EquipamentoDescricao(models.Model):
    codigo = models.CharField(max_length=5, verbose_name="Código", primary_key=True)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")

class EquipamentoCusto(models.Model):
    estado = models.CharField(max_length=2)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(12)])
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2020),
                                                  MaxValueValidator(2023)])
    desonerado = models.CharField(max_length=1)
    codigo = models.ForeignKey(EquipamentoDescricao, verbose_name="Código", on_delete=models.PROTECT)
    valor_aquisicao = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Valor de Aquisição")
    depreciacao = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Depreciação")
    oportunidade_capital = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Oportunidade de Capital")
    seguro_e_impostos = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Seguro e Impostos")
    manutencao = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Manutenção")
    operacao = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Operação")
    mao_de_obra_de_operacao = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Mão de Obra de Operação")
    custo_produtivo = models.DecimalField(max_digits=20, decimal_places=4, verbose_name="Custo Produtivo")
    custo_improdutivo = models.DecimalField(max_digits=20, decimal_places=4)

    class Meta:
        unique_together = ('estado', 'mes', 'ano', 'desonerado', 'codigo',)

class EquipamentoRelacaoComp(models.Model):
    comp = models.ForeignKey(Sicro, on_delete=models.CASCADE)
    codigo = models.ForeignKey(EquipamentoDescricao, verbose_name=("Código"), on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=20, decimal_places=5)
    utilizacao_operativa = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Utilização Operativa")
    utilizacao_improdutiva = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Utilização Improdutiva")

    class Meta:
        unique_together = ('comp', 'codigo',)

class MaterialDescricao(models.Model):
    codigo = models.CharField(max_length=5, verbose_name="Código", primary_key=True)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    unidade = models.CharField(max_length=10)

class MaterialCusto(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=2)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(12)])
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2020),
                                                  MaxValueValidator(2023)])
    desonerado = models.CharField(max_length=1)
    codigo = models.ForeignKey(MaterialDescricao, verbose_name="Código", on_delete=models.PROTECT)
    preco_unitario = models.DecimalField(max_digits=20, decimal_places=4, verbose_name="Preço Unitário")

class MaterialRelacaoComp(models.Model):
    id = models.AutoField(primary_key=True)
    comp = models.ForeignKey(Sicro, on_delete=models.CASCADE, verbose_name="Composição")
    codigo = models.ForeignKey(MaterialDescricao, verbose_name="Código", on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=20, decimal_places=5)
    tempo_fixo = models.ForeignKey(Sicro, on_delete=models.PROTECT, null=True, blank=True, related_name='tempos_fixos')
    quantidade_tempo_fixo = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)

    class Meta:
        unique_together = ('comp', 'codigo',)

class AtividadeAuxiliarRelacaoComp(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.ForeignKey(Sicro, on_delete=models.CASCADE, verbose_name='Código Composição')
    atividade_aux = models.ForeignKey(Sicro, on_delete=models.PROTECT, verbose_name='Código Atividade Auxiliar', related_name='atividades_auxiliares')
    quantidade = models.DecimalField(max_digits=20, decimal_places=5)
    tempo_fixo = models.ForeignKey(Sicro, on_delete=models.PROTECT, null=True, blank=True, related_name='tempos_fixos_aux')
    quantidade_tempo_fixo = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)

    class Meta:
        unique_together = ('codigo', 'atividade_aux',)
    
