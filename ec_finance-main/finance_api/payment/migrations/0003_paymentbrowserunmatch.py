# Generated by Django 3.2.10 on 2022-05-05 03:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0002_codatransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentBrowserUnmatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=200, null=True)),
                ('bank_account_nr', models.CharField(max_length=200, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('message', models.CharField(max_length=500, null=True)),
                ('invoice_nos', models.CharField(max_length=200, null=True)),
                ('remarks', models.CharField(max_length=200, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_mapped', models.BooleanField(default=False)),
                ('bank_name', models.CharField(max_length=200, null=True)),
                ('coda_file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='payment.codafile')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]