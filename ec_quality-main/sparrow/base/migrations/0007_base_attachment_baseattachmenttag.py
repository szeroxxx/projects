# Generated by Django 2.2.6 on 2023-01-20 17:01

import attachment.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attachment', '0001_initial'),
        ('base', '0006_auto_20221229_1028'),
    ]

    operations = [
        migrations.CreateModel(
            name='Base_Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=270)),
                ('uid', models.CharField(default=attachment.models.get_uid, max_length=50)),
                ('url', models.FileField(max_length=270, upload_to=attachment.models.update_filename)),
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
                ('object_id', models.IntegerField(blank=True, null=True)),
                ('file_type', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.PROTECT, to='attachment.FileType', verbose_name='File type')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BaseAttachmentTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Base_Attachment')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attachment.Tag')),
            ],
        ),
    ]
