# Generated by Django 2.2.6 on 2023-01-23 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0055_auto_20230120_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='panel_no',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
