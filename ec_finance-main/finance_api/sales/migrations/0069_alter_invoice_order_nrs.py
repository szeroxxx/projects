# Generated by Django 3.2.10 on 2023-01-03 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0068_collectionaction_is_cust_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='order_nrs',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
