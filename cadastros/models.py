from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here.
class Estado(models.Model):
    sigla = models.CharField(max_length=2)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.sigla
    
class Obra(models.Model):
    nome = models.CharField(max_length=150)
    ano = models.PositiveIntegerField(validators=[MinValueValidator(2000),
                                                  MaxValueValidator(2023)])
    tipo_de_obra = models.CharField(max_length=150)

    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
