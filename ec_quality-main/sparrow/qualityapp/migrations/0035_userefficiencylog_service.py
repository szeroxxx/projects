# Generated by Django 2.2.6 on 2022-11-11 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0034_auto_20221111_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='userefficiencylog',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='qualityapp.Service'),
        ),
    ]
