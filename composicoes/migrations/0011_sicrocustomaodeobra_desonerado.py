# Generated by Django 4.1.2 on 2023-04-19 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0010_alter_sicrocustomaodeobra_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='sicrocustomaodeobra',
            name='desonerado',
            field=models.CharField(default='N', max_length=1),
            preserve_default=False,
        ),
    ]