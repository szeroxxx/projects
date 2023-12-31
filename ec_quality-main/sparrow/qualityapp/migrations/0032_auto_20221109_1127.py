# Generated by Django 2.2.6 on 2022-11-09 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0031_order_import_order_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='userefficiencylog',
            name='extra_point',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userefficiencylog',
            name='layer_point',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userefficiencylog',
            name='prep_time',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='userefficiencylog',
            name='total_work_efficiency',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]
