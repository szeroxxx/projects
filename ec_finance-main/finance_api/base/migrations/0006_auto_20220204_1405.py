# Generated by Django 3.2.10 on 2022-02-04 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_codetable_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currency',
            name='symbol',
        ),
        migrations.AddField(
            model_name='currency',
            name='code',
            field=models.CharField(default=1, max_length=3, verbose_name='Currency code'),
            preserve_default=False,
        ),
    ]
