# Generated by Django 3.2.10 on 2022-02-07 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0016_auto_20220204_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionaction',
            name='is_legal',
            field=models.BooleanField(default=False),
        ),
    ]
