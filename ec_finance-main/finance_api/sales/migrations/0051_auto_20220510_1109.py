# Generated by Django 3.2.10 on 2022-05-10 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0050_auto_20220509_1609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='credit_limit',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='customer_credit_limit',
        ),
    ]
