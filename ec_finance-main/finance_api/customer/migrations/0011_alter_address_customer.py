# Generated by Django 3.2.10 on 2022-02-03 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_alter_address_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='address_customer', to='customer.customer'),
        ),
    ]
