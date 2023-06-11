# Generated by Django 3.2.10 on 2022-02-11 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0011_alter_address_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street_address1',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street_address2',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='account_number',
            field=models.CharField(blank=True, help_text='Number assigned by Accounting', max_length=30, null=True, verbose_name='Account number'),
        ),
    ]