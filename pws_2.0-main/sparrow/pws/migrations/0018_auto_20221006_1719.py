# Generated by Django 2.2.6 on 2022-10-06 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0017_order_order_in_exception'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_in_exception',
        ),
        migrations.AddField(
            model_name='orderexception',
            name='order_in_exception',
            field=models.BooleanField(default=False),
        ),
    ]
