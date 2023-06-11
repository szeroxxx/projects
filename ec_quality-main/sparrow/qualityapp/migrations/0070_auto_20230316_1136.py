# Generated by Django 2.2.6 on 2023-03-16 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0069_order_mail_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderexception',
            name='exception_status',
            field=models.CharField(choices=[('in_coming', 'In coming'), ('put_to_customer', 'Put to customer'), ('resolve', 'Resolve')], default='in_coming', max_length=100, null=True),
        ),
    ]