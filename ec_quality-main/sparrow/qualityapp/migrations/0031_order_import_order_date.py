# Generated by Django 2.2.6 on 2022-11-04 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0030_order_finished_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='import_order_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]