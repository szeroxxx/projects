# Generated by Django 2.2.6 on 2022-11-07 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_commenttype_remark_remark_attachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sysparameter',
            name='descr',
            field=models.CharField(blank=True, max_length=600, null=True, verbose_name='Description'),
        ),
    ]
