# Generated by Django 2.2.6 on 2022-11-10 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0032_auto_20221109_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='nonconformity',
            name='nc_from',
            field=models.CharField(blank=True, choices=[('schematic', 'Schematic'), ('footprint', 'Footprint'), ('placement', 'Placement'), ('routing', 'Routing'), ('gerber_release', 'Gerber Release'), ('analysis', 'Analysis'), ('incoming', 'Incoming'), ('BOM_incoming', 'BOM incoming'), ('SI', 'SI'), ('SICC', 'SICC'), ('BOM_CC', 'BOM CC'), ('FQC', 'FQC'), ('panel', 'Panel'), ('upload_panel', 'Upload Panel'), ('cancel', 'Cancel'), ('exception', 'Exception'), ('finished', 'Order Finished')], max_length=50, null=True),
        ),
    ]
