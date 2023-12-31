# Generated by Django 2.2.6 on 2022-09-30 10:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0010_auto_20220929_1853'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderallocationflow',
            name='allocation_id',
        ),
        migrations.AddField(
            model_name='orderallocationflow',
            name='allocation',
            field=models.CharField(blank=True, choices=[('pre_due_date', 'PreDueDate'), ('delivery_date', 'Delivery date')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='orderallocationflow',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderallocationflow',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
