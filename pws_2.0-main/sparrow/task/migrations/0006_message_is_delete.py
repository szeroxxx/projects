# Generated by Django 2.2.6 on 2022-12-20 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_delete',
            field=models.BooleanField(default=False, verbose_name='Is delete'),
        ),
    ]
