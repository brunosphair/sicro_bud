# Generated by Django 4.1.2 on 2023-04-17 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0007_alter_sicromaodeobra_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sicrocustomaodeobra',
            name='estado',
            field=models.CharField(max_length=2),
        ),
    ]
