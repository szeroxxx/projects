# Generated by Django 2.2.6 on 2023-02-13 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0061_auto_20230213_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='technicalhelp',
            name='attended_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
