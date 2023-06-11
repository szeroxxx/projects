# Generated by Django 3.2.10 on 2022-06-29 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0014_alter_paymentregistration_payment_difference_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='codatransaction',
            name='ec_coda_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paymentregistration',
            name='payment_difference_type',
            field=models.CharField(choices=[('OutStanding', 'Outstanding'), ('Bank Charges', 'Bank Charges'), ('Discount', 'Discount'), ('Write Off', 'Write off'), ('OverPaid', 'OverPaid'), ('INVCLOSED', 'Close')], max_length=100, null=True),
        ),
    ]
