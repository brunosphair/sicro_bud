# Generated by Django 4.1.2 on 2023-04-12 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0003_remove_estado_id_obra_mes_alter_estado_sigla'),
        ('composicoes', '0003_sicrocustomaodeobra'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sicrocustomaodeobra',
            unique_together={('estado', 'mes', 'ano', 'codigo')},
        ),
    ]
