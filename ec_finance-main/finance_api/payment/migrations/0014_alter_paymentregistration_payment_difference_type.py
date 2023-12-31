# Generated by Django 3.2.10 on 2022-06-20 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_auto_20220606_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentregistration',
            name='payment_difference_type',
            field=models.CharField(choices=[('outstanding', 'Outstanding'), ('bank_charges', 'Bank Charges'), ('discount', 'Discount'), ('write_off', 'Write off'), ('over_paid', 'OverPaid'), ('Close', 'Close')], max_length=100, null=True),
        ),
    ]
