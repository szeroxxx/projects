# Generated by Django 3.2.10 on 2022-03-17 12:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0012_auto_20220211_1025'),
        ('sales', '0032_auto_20220317_1143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='ec_delivery_id',
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_iddress',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customer.address'),
        ),
    ]
