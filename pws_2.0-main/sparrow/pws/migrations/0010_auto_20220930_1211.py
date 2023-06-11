# Generated by Django 2.2.6 on 2022-09-30 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0009_auto_20220930_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderexception',
            name='exception_status',
            field=models.CharField(choices=[('in_coming', 'In coming'), ('put_to_customer', 'Put to customer')], default='in_coming', max_length=100, null=True),
        ),
    ]
