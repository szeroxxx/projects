# Generated by Django 3.2.10 on 2022-06-14 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditlog', '0004_auditlog_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='document_no',
            field=models.CharField(default='', max_length=45, null=True),
        ),
    ]
