# Generated by Django 3.2.10 on 2022-01-31 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_auto_20220131_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='last_order_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
