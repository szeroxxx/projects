# Generated by Django 3.2.10 on 2022-02-01 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_alter_address_street_no'),
        ('sales', '0005_auto_20220201_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionaction',
            name='action_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('call_due', 'Call due'), ('call_done', 'Call done'), ('finished', 'Finished'), ('legal_action', 'Legal Action')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='scheduleritem',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='scheduleritem_customer', to='customer.customer'),
            preserve_default=False,
        ),
    ]
