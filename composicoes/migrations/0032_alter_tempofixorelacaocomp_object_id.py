# Generated by Django 4.1.2 on 2023-04-26 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0031_alter_tempofixorelacaocomp_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempofixorelacaocomp',
            name='object_id',
            field=models.CharField(max_length=7),
        ),
    ]
