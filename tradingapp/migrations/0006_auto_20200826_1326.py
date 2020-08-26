# Generated by Django 2.2 on 2020-08-26 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tradingapp', '0005_auto_20200826_0820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='tradingapp.Stock'),
        ),
    ]