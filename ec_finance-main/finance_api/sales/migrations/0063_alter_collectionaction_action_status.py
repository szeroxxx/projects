# Generated by Django 3.2.10 on 2022-06-22 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0062_auto_20220622_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionaction',
            name='action_status',
            field=models.CharField(choices=[('done', 'Processed'), ('due', 'Follow up'), ('completed', 'Completed'), ('finished', 'Finished'), ('pending', 'Pending')], max_length=100, null=True),
        ),
    ]
