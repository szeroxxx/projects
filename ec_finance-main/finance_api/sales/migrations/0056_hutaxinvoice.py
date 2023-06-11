# Generated by Django 3.2.10 on 2022-06-08 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0055_invoice_paid_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='HutaxInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hu_status', models.CharField(max_length=50)),
                ('transaction_id', models.CharField(max_length=200)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('file_path', models.TextField(default='')),
                ('index_number', models.IntegerField(null=True)),
                ('order_count', models.IntegerField(null=True)),
                ('status_time', models.DateTimeField(blank=True, null=True)),
                ('result', models.CharField(max_length=250, null=True)),
                ('error', models.TextField(default='')),
                ('original_invoice_number', models.CharField(max_length=150)),
                ('vat_no', models.CharField(max_length=25, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hutaxinvoice_invoice', to='sales.invoice')),
            ],
        ),
    ]