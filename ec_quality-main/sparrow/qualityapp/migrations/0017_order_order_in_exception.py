# Generated by Django 2.2.6 on 2022-10-06 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0016_auto_20221004_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_in_exception',
            field=models.BooleanField(default=False),
        ),
    ]