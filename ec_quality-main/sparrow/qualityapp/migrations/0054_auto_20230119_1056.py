# Generated by Django 2.2.6 on 2023-01-19 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0053_auto_20230111_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='doc',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='operator',
            name='doj',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='operator',
            name='dor',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='operator',
            name='remark',
            field=models.TextField(blank=True, default=''),
        ),
    ]
