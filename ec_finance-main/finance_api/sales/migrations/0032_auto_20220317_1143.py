# Generated by Django 3.2.10 on 2022-03-17 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0031_auto_20220226_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduler',
            name='ec_scheduler_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectionaction',
            name='action_status',
            field=models.CharField(choices=[('done', 'Processed'), ('due', 'Follow up'), ('completed', 'Completed'), ('finished', 'Finished')], default='pending', max_length=100),
        ),
        migrations.AlterField(
            model_name='collectionaction',
            name='action_type',
            field=models.CharField(blank=True, choices=[('call', 'Call'), ('email', 'Email'), ('chat', 'Chat'), ('offline_message', 'Offline message'), ('remarks', 'Remarks'), ('follow_up', 'Follow up')], max_length=100, null=True),
        ),
    ]
