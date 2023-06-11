# Generated by Django 2.2.6 on 2022-09-30 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0008_orderexception_predefineexceptionproblem_predefineexceptionsolution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderexception',
            name='exception_status',
            field=models.CharField(choices=[('in_coming', 'In coming'), ('put_to_customer', 'Put to customer')], default='in coming', max_length=100, null=True),
        ),
    ]
