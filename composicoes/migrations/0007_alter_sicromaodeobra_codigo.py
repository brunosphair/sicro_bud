# Generated by Django 4.1.2 on 2023-04-15 01:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0006_remove_descricaomaodeobra_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sicromaodeobra',
            name='codigo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='composicoes.descricaomaodeobra', verbose_name='Código'),
        ),
    ]
