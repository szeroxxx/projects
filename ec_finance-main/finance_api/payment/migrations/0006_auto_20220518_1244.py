# Generated by Django 3.2.10 on 2022-05-18 07:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_alter_codafile_created_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodaCustomerMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField(null=True)),
                ('customer_name', models.CharField(max_length=200, null=True)),
                ('remark', models.TextField(default='')),
                ('bank_customer_name', models.CharField(max_length=200, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('account_no', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='paymentbrowserunmatch',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
