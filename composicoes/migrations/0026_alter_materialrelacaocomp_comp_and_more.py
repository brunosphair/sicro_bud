# Generated by Django 4.1.2 on 2023-04-26 00:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0025_materialrelacaocomp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialrelacaocomp',
            name='comp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='composicoes.sicro', verbose_name='Composição'),
        ),
        migrations.AlterUniqueTogether(
            name='materialrelacaocomp',
            unique_together={('comp', 'codigo')},
        ),
        migrations.CreateModel(
            name='AtividadeAuxiliarRelacaoComp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.DecimalField(decimal_places=5, max_digits=20)),
                ('atividade_aux', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='atividades_auxiliares', to='composicoes.sicro', verbose_name='Código Atividade Auxiliar')),
                ('codigo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='composicoes.sicro', verbose_name='Código Composição')),
            ],
            options={
                'unique_together': {('codigo', 'atividade_aux')},
            },
        ),
    ]
