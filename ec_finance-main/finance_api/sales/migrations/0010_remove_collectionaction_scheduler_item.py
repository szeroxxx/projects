# Generated by Django 3.2.10 on 2022-02-02 12:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_auto_20220202_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionaction',
            name='scheduler_item',
        ),
    ]
