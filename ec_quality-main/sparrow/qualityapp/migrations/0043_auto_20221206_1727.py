# Generated by Django 2.2.6 on 2022-12-06 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0042_auto_20221205_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userefficiencylog',
            name='prep_time',
            field=models.CharField(blank=True, max_length=56, null=True),
        ),
    ]
