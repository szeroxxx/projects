# Generated by Django 3.2.10 on 2022-06-06 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_auto_20220530_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='codafile',
            name='compared_xml_string2',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='codafile',
            name='xml_string1',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
