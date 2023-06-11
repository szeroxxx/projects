# Generated by Django 2.2.6 on 2020-03-25 12:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Task type')),
                ('code', models.CharField(blank=True, max_length=100, null=True)),
                ('icon', models.CharField(blank=True, max_length=500, null=True, verbose_name='Icon')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('entity_id', models.IntegerField(blank=True, null=True, verbose_name='ID of the object')),
                ('related_to', models.CharField(blank=True, max_length=200, null=True, verbose_name='Related to')),
                ('description', models.CharField(blank=True, default='', max_length=200, verbose_name='Description')),
                ('due_date', models.DateTimeField(blank=True, null=True, verbose_name='Due date')),
                ('status', models.CharField(blank=True, choices=[('not_started', 'Not started'), ('in_progress', 'In progress'), ('completed', 'Completed')], default='not_started', max_length=40, null=True)),
                ('priority', models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='low', max_length=40, null=True)),
                ('email_notification', models.BooleanField(default=False, verbose_name='Email notification')),
                ('private', models.BooleanField(default=False, verbose_name='Private task')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('due_mail_sent_time', models.DateTimeField(null=True)),
                ('reminder_on', models.DateTimeField(blank=True, null=True)),
                ('reminder_on_text', models.CharField(blank=True, max_length=50, null=True)),
                ('has_reminder_sent', models.BooleanField(default=False)),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='Remarks')),
                ('assign_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='task_assign_to', to=settings.AUTH_USER_MODEL, verbose_name='Assign to')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('task_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='task.TaskType', verbose_name='Task type')),
            ],
        ),
    ]
