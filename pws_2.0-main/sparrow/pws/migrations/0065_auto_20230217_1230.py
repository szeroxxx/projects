# Generated by Django 2.2.6 on 2023-02-17 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0064_order_act_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='userefficiencylog',
            name='preparation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='nonconformity',
            name='nc_from',
            field=models.CharField(blank=True, choices=[('schematic', 'Schematic'), ('footprint', 'Footprint'), ('placement', 'Placement'), ('routing', 'Routing'), ('gerber_release', 'Gerber Release'), ('analysis', 'Analysis'), ('incoming', 'Incoming'), ('BOM_incoming', 'BOM incoming'), ('SI', 'SI'), ('SICC', 'SICC'), ('BOM_CC', 'BOM CC'), ('FQC', 'FQC'), ('panel', 'Panel'), ('upload_panel', 'Upload Panel'), ('cancel', 'Cancel'), ('exception', 'Exception'), ('ppa_exception', 'PPA Exception'), ('finished', 'Order Finish')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('schematic', 'Schematic'), ('footprint', 'Footprint'), ('placement', 'Placement'), ('routing', 'Routing'), ('gerber_release', 'Gerber Release'), ('analysis', 'Analysis'), ('incoming', 'Incoming'), ('BOM_incoming', 'BOM incoming'), ('SI', 'SI'), ('SICC', 'SICC'), ('BOM_CC', 'BOM CC'), ('FQC', 'FQC'), ('panel', 'Panel'), ('upload_panel', 'Upload Panel'), ('cancel', 'Cancel'), ('exception', 'Exception'), ('ppa_exception', 'PPA Exception'), ('finished', 'Order Finish')], max_length=50, null=True),
        ),
    ]
