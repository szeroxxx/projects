# Generated by Django 2.2.6 on 2022-11-03 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0029_auto_20221102_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='finished_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
