# Generated by Django 2.2.6 on 2020-05-27 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_company_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ec_user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
