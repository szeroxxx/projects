# Generated by Django 2.2.6 on 2023-04-04 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0076_nonconformitydetail_audit_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performanceindex',
            name='years_of_experience',
            field=models.CharField(choices=[('6_month', '< 6 months'), ('1_year', 'more than 6 and < 1 year'), ('2_year', 'more than a year and < 2 years'), ('3_years', '> 2 years')], max_length=100, null=True),
        ),
    ]
