# Generated by Django 2.2.6 on 2022-11-30 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0039_auto_20221128_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userefficiencylog',
            name='prep_time',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='userefficiencylog',
            name='total_work_efficiency',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
