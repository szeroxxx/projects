# Generated by Django 3.2.10 on 2022-07-13 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0065_invoice_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]
