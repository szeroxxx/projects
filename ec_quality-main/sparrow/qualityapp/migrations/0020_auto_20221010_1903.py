# Generated by Django 2.2.6 on 2022-10-10 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qualityapp", "0019_auto_20221007_1904"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="nonconformity",
            name="nc_remarks",
        ),
        migrations.AddField(
            model_name="nonconformity",
            name="nc_type",
            field=models.CharField(
                choices=[
                    ("rejection", "Rejection"),
                    ("remark", "Remark"),
                    ("bad_exc", "Bad Exc "),
                    ("training", "Training"),
                    ("remark_internal", "Remark-internal"),
                    ("not_to_count", "Not to count"),
                    ("cust_mod", "Cust Mod"),
                    ("update", "Update"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]
