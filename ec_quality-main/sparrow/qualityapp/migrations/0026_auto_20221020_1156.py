# Generated by Django 2.2.6 on 2022-10-20 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0025_auto_20221019_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_format',
            field=models.CharField(blank=True, choices=[('Single PCB', 'Single PCB'), ('Panel', 'Panel')], max_length=50, null=True),
        ),
    ]
