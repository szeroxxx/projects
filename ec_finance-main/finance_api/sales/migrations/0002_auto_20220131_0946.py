# Generated by Django 3.2.10 on 2022-01-31 04:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_auto_20220131_0946'),
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionaction',
            name='is_legal_action',
        ),
        migrations.RemoveField(
            model_name='collectionaction',
            name='scheduler',
        ),
        migrations.RemoveField(
            model_name='scheduler',
            name='is_legal_action',
        ),
        migrations.RemoveField(
            model_name='scheduler',
            name='scheduler_name',
        ),
        migrations.RemoveField(
            model_name='scheduler',
            name='status',
        ),
        migrations.RemoveField(
            model_name='scheduleritem',
            name='invoice',
        ),
        migrations.AddField(
            model_name='collectionaction',
            name='scheduler_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='action_scheduler', to='sales.scheduleritem'),
        ),
        migrations.AddField(
            model_name='scheduler',
            name='name',
            field=models.CharField(max_length=200, null=True, verbose_name='Scheduler Name'),
        ),
        migrations.AddField(
            model_name='scheduleritem',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('call_due', 'Call due'), ('call_done', 'Call done'), ('finished', 'Finished'), ('legal_action', 'Legal Action')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='scheduleritem',
            name='total_invoice',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectionaction',
            name='action_type',
            field=models.CharField(blank=True, choices=[('call', 'Call'), ('chat', 'Chat'), ('offline_message', 'Offline message'), ('ticket', 'Ticket'), ('plan_follow_up', 'Plan Follow up')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customer.user'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='created_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='scheduler',
            name='created_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='scheduleritem',
            name='scheduler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='scheduler', to='sales.scheduler'),
        ),
        migrations.CreateModel(
            name='SchedulerInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice', models.ManyToManyField(related_name='scheduler_invoice', to='sales.Invoice')),
                ('scheduler_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduler_item', to='sales.scheduleritem')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_numbre', models.IntegerField(blank=True, null=True)),
                ('order_number', models.CharField(blank=True, max_length=100, null=True)),
                ('order_unit_value', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('invoice_amount', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('ord_trp_value', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('order_vnit_value_Curr', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('ord_trp_value_curr', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('invoice_amount_curr', models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ('is_reduce_vat', models.BooleanField(default=False)),
                ('invoice_ref', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice', to='sales.invoice')),
            ],
        ),
    ]