# Generated by Django 3.2.10 on 2022-01-31 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_scheduler_created_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleritem',
            name='is_legal',
            field=models.BooleanField(default=False),
        ),
    ]
