# Generated by Django 4.1.2 on 2023-04-25 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0020_rename_custoequipamento_equipamentocusto_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialDescricao',
            fields=[
                ('codigo', models.CharField(max_length=7, primary_key=True, serialize=False, verbose_name='Código')),
                ('descricao', models.CharField(max_length=255, verbose_name='Descrição')),
            ],
        ),
    ]