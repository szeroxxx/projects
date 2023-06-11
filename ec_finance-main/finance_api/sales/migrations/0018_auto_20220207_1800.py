# Generated by Django 3.2.10 on 2022-02-07 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_codetable_is_deleted'),
        ('sales', '0017_collectionaction_is_legal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='invoice_type',
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_type_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectioninvoice',
            name='action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collectioninvoice_action', to='sales.collectionaction'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_close_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_created_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_due_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='last_rem_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_tracking_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='secondry_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_secondry_status', to='base.codetable'),
        ),
    ]
