# Generated by Django 2.2.6 on 2022-10-18 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0023_layer'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_img',
            field=models.TextField(default=''),
        ),
    ]
