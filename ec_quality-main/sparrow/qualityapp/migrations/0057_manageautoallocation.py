# Generated by Django 2.2.6 on 2023-01-31 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0056_auto_20230123_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManageAutoAllocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_start_time', models.TimeField(blank=True, null=True)),
                ('stop_end_time', models.TimeField(blank=True, null=True)),
            ],
        ),
    ]
