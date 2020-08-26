# Generated by Django 2.2 on 2020-08-26 00:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tradingapp', '0003_auto_20200826_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='tradingapp.Stock'),
        ),
    ]
