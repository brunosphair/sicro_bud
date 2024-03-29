# Generated by Django 4.1.2 on 2023-04-26 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0034_alter_materialrelacaocomp_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividadeauxiliarrelacaocomp',
            name='quantidade_tempo_fixo',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='atividadeauxiliarrelacaocomp',
            name='tempo_fixo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tempos_fixos_aux', to='composicoes.sicro'),
        ),
    ]
