# Generated by Django 4.2.17 on 2025-02-28 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carniceria', '0021_articulo_sucursal_habilitado_articulo_empresa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo_sucursal',
            name='habilitado',
            field=models.CharField(max_length=1),
        ),
    ]
