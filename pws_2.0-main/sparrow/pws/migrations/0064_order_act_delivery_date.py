# Generated by Django 2.2.6 on 2023-02-16 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0063_userefficiencylog_knowledge_leaders'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='act_delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
