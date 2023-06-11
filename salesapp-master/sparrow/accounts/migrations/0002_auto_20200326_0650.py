# Generated by Django 2.2.6 on 2020-03-26 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='partner_id',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='purchase_plan_settings',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_type',
            field=models.IntegerField(choices=[(1, 'Internal'), (2, 'Customer')], null=True, verbose_name='User type'),
        ),
    ]