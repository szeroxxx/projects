# Generated by Django 3.2.10 on 2022-05-12 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0051_auto_20220510_1109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='remark',
        ),
        migrations.AddField(
            model_name='scheduleritem',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]
