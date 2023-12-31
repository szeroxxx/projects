# Generated by Django 3.2.10 on 2022-02-01 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_alter_address_customer'),
        ('sales', '0007_auto_20220201_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='customer',
            field=models.ForeignKey(default=2858, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_customer', to='customer.customer'),
            preserve_default=False,
        ),
    ]
