# Generated by Django 2.2.6 on 2022-11-11 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0033_nonconformity_nc_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='in_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderallocationflow',
            name='allocation',
            field=models.CharField(blank=True, choices=[
                ('pre_due_date', 'Preparation due date'),
                ('delivery_date', 'Delivery date'),
                ('systemin_time', 'Systemin time'),
                ('total_minutes', 'Total minutes'),
                ('order_date', 'Order date'),
                ('delivery_and_order_date', 'Delivery date and Order date')
            ], max_length=50, null=True),
        ),
    ]
