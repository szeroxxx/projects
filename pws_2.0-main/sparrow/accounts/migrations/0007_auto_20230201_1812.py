# Generated by Django 2.2.6 on 2023-02-01 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_rolegroup_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpermission',
            name='is_customer_user',
            field=models.BooleanField(default=False, verbose_name='View customer user'),
        ),
        migrations.AddField(
            model_name='contentpermission',
            name='is_operator',
            field=models.BooleanField(default=False, verbose_name='View operator'),
        ),
    ]
