# Generated by Django 2.2.6 on 2022-09-29 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0008_orderexception_predefineexceptionproblem_predefineexceptionsolution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operator',
            name='permanent_shift',
            field=models.CharField(blank=True, choices=[('first_shift', 'First shift'), ('second_shift', 'Second shift'), ('third_shift', 'Third shift'), ('general_shift', 'General shift')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='operator',
            name='shift',
            field=models.CharField(blank=True, choices=[('first_shift', 'First shift'), ('second_shift', 'Second shift'), ('third_shift', 'Third shift'), ('general_shift', 'General shift')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('schematic', 'Schematic'), ('footprint', 'Footprint'), ('placement', 'Placement'), ('routing', 'Routing'), ('gerber _release', 'Gerber Release'), ('analysis', 'Analysis'), ('incoming', 'Incoming'), ('bom_incoming', 'BOM incoming'), ('SI', 'SI'), ('SICC', 'SICC'), ('BOM CC', 'BOM CC'), ('FQC', 'FQC'), ('Panel', 'panel'), ('upload_panel', 'Upload Panel')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orderexception',
            name='order_status',
            field=models.CharField(choices=[('schematic', 'Schematic'), ('footprint', 'Footprint'), ('placement', 'Placement'), ('routing', 'Routing'), ('gerber _release', 'Gerber Release'), ('analysis', 'Analysis'), ('incoming', 'Incoming'), ('bom_incoming', 'BOM incoming'), ('SI', 'SI'), ('SICC', 'SICC'), ('BOM CC', 'BOM CC'), ('FQC', 'FQC'), ('Panel', 'panel'), ('upload_panel', 'Upload Panel')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='ordertechparameter',
            name='edge_connector_gold_surface',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
