# Generated by Django 2.2 on 2020-08-26 00:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tradingapp', '0004_auto_20200826_0805'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='stock',
            options={'ordering': ('name',)},
        ),
    ]
