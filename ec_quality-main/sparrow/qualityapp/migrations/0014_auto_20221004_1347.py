# Generated by Django 2.2.6 on 2022-10-04 13:47

import attachment.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attachment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qualityapp', '0013_merge_20221004_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('schematic', 'Schematic'), ('footprint', 'Footprint'), ('placement', 'Placement'), ('routing', 'Routing'), ('gerber_release', 'Gerber Release'), ('analysis', 'Analysis'), ('incoming', 'Incoming'), ('bom_incoming', 'BOM incoming'), ('SI', 'SI'), ('SICC', 'SICC'), ('BOM_CC', 'BOM CC'), ('FQC', 'FQC'), ('panel', 'Panel'), ('upload_panel', 'Upload Panel'), ('cancel', 'Cancel')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orderexception',
            name='order_status',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Order_Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150)),
                ('uid', models.CharField(default=attachment.models.get_uid, max_length=50)),
                ('object_id', models.IntegerField()),
                ('url', models.FileField(upload_to=attachment.models.update_filename)),
                ('title', models.CharField(default='', max_length=150)),
                ('subject', models.CharField(default='', max_length=50)),
                ('source_doc', models.CharField(default='', max_length=50)),
                ('description', models.TextField(default='')),
                ('size', models.IntegerField(default=0)),
                ('ip_addr', models.CharField(default='', max_length=45)),
                ('deleted', models.BooleanField(default=False)),
                ('checksum', models.CharField(default='', max_length=45)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('doc_type', models.CharField(choices=[('general', 'General'), ('invoice', 'Invoice'), ('order', 'Order')], default='gen', max_length=20, verbose_name='Doc Type')),
                ('is_public', models.BooleanField(default=False)),
                ('file_type', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.PROTECT, to='attachment.FileType', verbose_name='File type')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
