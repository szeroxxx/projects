# Generated by Django 3.2.10 on 2022-02-03 07:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_alter_customer_invoice_lang'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='contact_number',
        ),
    ]
