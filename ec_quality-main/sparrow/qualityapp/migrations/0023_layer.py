# Generated by Django 2.2.6 on 2022-10-14 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0022_auto_20221013_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
            ],
        ),
    ]