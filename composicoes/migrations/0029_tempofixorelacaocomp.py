# Generated by Django 4.1.2 on 2023-04-26 02:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('composicoes', '0028_alter_materialcusto_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempoFixoRelacaoComp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('quantidade', models.DecimalField(decimal_places=5, max_digits=20)),
                ('codigo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='composicoes.sicro', verbose_name='Código Composição')),
                ('content_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'composicoes'), ('model', 'sicro')), models.Q(('app_label', 'composicoes'), ('model', 'materialdescricao')), _connector='OR'), on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype', verbose_name='Código Item Transportado')),
                ('tempo_fixo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tempo_fixos', to='composicoes.sicro', verbose_name='Código Tempo Fixo')),
            ],
        ),
    ]