# Generated by Django 4.1.2 on 2023-04-25 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0022_alter_materialdescricao_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialdescricao',
            name='unidade',
            field=models.CharField(default='error', max_length=10),
            preserve_default=False,
        ),
    ]
