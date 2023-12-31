# Generated by Django 2.2.6 on 2023-02-13 18:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qualityapp', '0059_orderexception_is_si_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechnicalHelp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('attend', 'Attend')], default='open', max_length=100, null=True)),
                ('attended_on', models.DateTimeField(auto_now_add=True)),
                ('attended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='attended_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
