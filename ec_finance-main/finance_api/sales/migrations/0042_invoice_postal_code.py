# Generated by Django 3.2.10 on 2022-04-28 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0041_auto_20220428_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]