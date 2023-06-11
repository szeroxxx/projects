# Generated by Django 3.2.10 on 2022-06-08 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0056_hutaxinvoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeppolInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pe_status', models.CharField(max_length=50)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('result', models.CharField(blank=True, max_length=250, null=True)),
                ('error', models.TextField(default='')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='peppolinvoice_invoice', to='sales.invoice')),
            ],
        ),
    ]