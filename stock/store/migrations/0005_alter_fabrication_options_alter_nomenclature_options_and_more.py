# Generated by Django 5.0.6 on 2025-03-22 23:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_item_is_finished_product'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fabrication',
            options={},
        ),
        migrations.AlterModelOptions(
            name='nomenclature',
            options={},
        ),
        migrations.AlterField(
            model_name='nomenclature',
            name='component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='used_in_nomenclatures', to='store.item', verbose_name='Matière première'),
        ),
        migrations.AlterField(
            model_name='nomenclature',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nomenclatures', to='store.item', verbose_name='Produit fini'),
        ),
    ]
