# Generated by Django 2.2.6 on 2022-12-06 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0043_auto_20221206_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userefficiencylog',
            name='prep_time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]