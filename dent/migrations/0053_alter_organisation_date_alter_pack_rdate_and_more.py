# Generated by Django 4.0.3 on 2022-05-24 09:32

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0052_rename_code_pack_status_remove_pack_head_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 24, 15, 2, 34, 470729)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 24, 15, 2, 34, 478707)),
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rdate', models.DateTimeField(default=datetime.datetime(2022, 5, 24, 15, 2, 34, 478707))),
                ('type', models.CharField(max_length=200)),
                ('scans', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=200)),
                ('validity', models.IntegerField(blank=True, null=True)),
                ('applied', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]
