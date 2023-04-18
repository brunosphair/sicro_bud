from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here.
    
class Sicro(models.Model):
    codigo = models.CharField(max_length=7, primary_key=True, verbose_name="Código")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    produtividade = models.DecimalField(max_digits=20, decimal_places=4)
    unidade = models.CharField(max_length=10)
    fic = models.DecimalField(max_digits=6, decimal_places=5)

    def __str__(self):
        return self.descricao

class DescricaoMaodeObra(models.Model):
    codigo = models.CharField(max_length=5, verbose_name="Código", primary_key=True)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    unidade = models.CharField(max_length=10)

class SicroCustoMaodeObra(models.Model):
    estado = models.CharField(max_length=2)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(12)])
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2020),
                                                  MaxValueValidator(2023)])
    codigo = models.ForeignKey(DescricaoMaodeObra, verbose_name="Código", on_delete=models.PROTECT)
    salario = models.DecimalField(max_digits=20, decimal_places=4, verbose_name="Salário")
    engargos_totais = models.DecimalField(max_digits=7, decimal_places=6)
    custo = models.DecimalField(max_digits=20, decimal_places=4)
    periculosidade_insalubridade = models.DecimalField(max_digits=7, decimal_places=6, verbose_name="Periculosidade/Insalubridade")

    class Meta:
        unique_together = ('estado', 'mes', 'ano', 'codigo',)

class SicroMaodeObra(models.Model):
    comp = models.ForeignKey(Sicro, on_delete=models.CASCADE)
    codigo = models.ForeignKey(DescricaoMaodeObra, verbose_name="Código", on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=20, decimal_places=5)

    class Meta:
        unique_together = ('comp', 'codigo',)