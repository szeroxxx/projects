# Generated by Django 2.2.6 on 2022-09-22 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0002_auto_20220921_1256'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderflowmapping',
            name='process',
        ),
        migrations.AddField(
            model_name='orderflowmapping',
            name='process_ids',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]