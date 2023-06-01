from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from composicoes.models import Sicro, CompFIC

# Create your models here.
class EstadoAtualizado(models.Model):
    sigla = models.CharField(max_length=2, primary_key=True)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.sigla


class Obra(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(12)],
                                                  verbose_name= "Mês de referência")
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2000),
                                                  MaxValueValidator(2023)],
                                                  verbose_name= "Ano de referência")
    tipo_de_obra = models.CharField(max_length=150)

    estado = models.ForeignKey(EstadoAtualizado, on_delete=models.PROTECT)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class CompsObra(models.Model):
    id = models.AutoField(primary_key=True)
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE)
    composicao = models.ForeignKey(Sicro, on_delete=models.PROTECT)
