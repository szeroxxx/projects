# Generated by Django 3.2.10 on 2022-02-12 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='File type name')),
                ('code', models.CharField(max_length=30, verbose_name='File type code')),
                ('description', models.CharField(default='', max_length=200, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
