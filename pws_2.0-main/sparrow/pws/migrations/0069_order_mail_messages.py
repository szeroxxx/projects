# Generated by Django 2.2.6 on 2023-02-24 12:22

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0068_userefficiencylog_operator_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='mail_messages',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
