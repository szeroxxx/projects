# Generated by Django 2.2.6 on 2023-03-30 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0072_performanceindex_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderexception',
            name='remarks',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
