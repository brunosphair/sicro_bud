# Generated by Django 4.1.2 on 2023-04-17 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0008_alter_sicrocustomaodeobra_estado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sicrocustomaodeobra',
            name='descricao',
        ),
    ]
