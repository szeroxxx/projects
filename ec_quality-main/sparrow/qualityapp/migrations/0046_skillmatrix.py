# Generated by Django 2.2.6 on 2022-12-19 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qualityapp', '0045_companyuser_is_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillMatrix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator_ids', models.CharField(blank=True, max_length=4000, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='skillmatrix_company', to='qualityapp.Company')),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='qualityapp.OrderProcess')),
            ],
        ),
    ]
