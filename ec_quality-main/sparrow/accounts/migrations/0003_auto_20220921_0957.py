# Generated by Django 2.2.6 on 2022-09-21 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20220920_0928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='company_ids',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='ec_user',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='group_type',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='permanent_shift',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='shift',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user_group',
        ),
        migrations.AlterField(
            model_name='mainmenu',
            name='company_code',
            field=models.IntegerField(blank=True, help_text='Specify company code if this menu is specific to company', null=True, verbose_name='Company Code'),
        ),
        migrations.AlterField(
            model_name='mainmenu',
            name='launcher_sequence',
            field=models.IntegerField(blank=True, default=0, help_text='Specify the order of menu icons.', null=True, verbose_name='Launcher Sequence'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_type',
            field=models.IntegerField(choices=[('1', 'Internal'), ('2', 'Customer')], null=True, verbose_name='User type'),
        ),
    ]
