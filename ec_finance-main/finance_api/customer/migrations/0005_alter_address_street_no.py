# Generated by Django 3.2.10 on 2022-02-01 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_auto_20220201_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street_no',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
