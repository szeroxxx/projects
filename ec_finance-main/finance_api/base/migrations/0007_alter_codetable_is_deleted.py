# Generated by Django 3.2.10 on 2022-02-04 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20220204_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codetable',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
