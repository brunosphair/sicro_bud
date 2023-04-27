# Generated by Django 4.1.2 on 2023-04-20 00:00

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0013_descricaoequipamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustoEquipamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(max_length=2)),
                ('mes', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('ano', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(2020), django.core.validators.MaxValueValidator(2023)])),
                ('desonerado', models.CharField(max_length=1)),
                ('valor_aquisicao', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Valor de Aquisição')),
                ('depreciacao', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Depreciação')),
                ('oportunidade_capital', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Oportunidade de Capital')),
                ('seguro_e_impostos', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Seguro e Impostos')),
                ('manutencao', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Manutenção')),
                ('operacao', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Operação')),
                ('mao_de_obra_de_operacao', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Mão de Obra de Operação')),
                ('custo_produtivo', models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Custo Produtivo')),
                ('custo_improdutivo', models.DecimalField(decimal_places=4, max_digits=20)),
                ('codigo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='composicoes.descricaoequipamento', verbose_name='Código')),
            ],
        ),
    ]