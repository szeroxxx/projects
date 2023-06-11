# Generated by Django 2.2.6 on 2022-10-03 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0011_auto_20220930_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoardThickness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='orderexception',
            name='last_reminder_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderexception',
            name='total_reminder',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ordertechparameter',
            name='material_tg',
            field=models.CharField(blank=True, choices=[('tg_145-150', '145-150 ºC'), ('tg_170-180', '170-180 ºC')], max_length=100, null=True),
        ),
    ]
