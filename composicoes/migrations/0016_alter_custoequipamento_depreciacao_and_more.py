# Generated by Django 4.1.2 on 2023-04-20 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0015_alter_custoequipamento_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custoequipamento',
            name='depreciacao',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Depreciação'),
        ),
        migrations.AlterField(
            model_name='custoequipamento',
            name='manutencao',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Manutenção'),
        ),
        migrations.AlterField(
            model_name='custoequipamento',
            name='mao_de_obra_de_operacao',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Mão de Obra de Operação'),
        ),
        migrations.AlterField(
            model_name='custoequipamento',
            name='operacao',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Operação'),
        ),
        migrations.AlterField(
            model_name='custoequipamento',
            name='oportunidade_capital',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Oportunidade de Capital'),
        ),
        migrations.AlterField(
            model_name='custoequipamento',
            name='seguro_e_impostos',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Seguro e Impostos'),
        ),
        migrations.AlterField(
            model_name='custoequipamento',
            name='valor_aquisicao',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True, verbose_name='Valor de Aquisição'),
        ),
    ]
