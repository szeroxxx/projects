# Generated by Django 3.2.10 on 2022-02-09 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0022_invoice_ec_delivery_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='invoice_address',
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_iddress_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
