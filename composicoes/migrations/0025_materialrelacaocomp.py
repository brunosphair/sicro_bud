# Generated by Django 4.1.2 on 2023-04-25 01:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('composicoes', '0024_materialcusto'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialRelacaoComp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.DecimalField(decimal_places=5, max_digits=20)),
                ('codigo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='composicoes.materialdescricao', verbose_name='Código')),
                ('comp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='composicoes.sicro')),
            ],
        ),
    ]
