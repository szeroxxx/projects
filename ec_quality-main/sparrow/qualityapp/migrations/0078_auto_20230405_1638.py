# Generated by Django 2.2.6 on 2023-04-05 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0077_auto_20230404_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='userefficiencylog',
            name='minimum_efficiency',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userefficiencylog',
            name='target_efficiency',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
