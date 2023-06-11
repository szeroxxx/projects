# Generated by Django 2.2.6 on 2022-12-19 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pws', '0044_auto_20221206_1907'),
        ('task', '0004_task_general'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False, verbose_name='Is read')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('read_on', models.DateTimeField(blank=True, null=True)),
                ('operator_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pws.Operator')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='task.Task')),
            ],
        ),
    ]
