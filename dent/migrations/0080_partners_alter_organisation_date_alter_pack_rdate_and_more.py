# Generated by Django 4.0.3 on 2022-07-15 05:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0079_report_driveid_report_drivelink_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partners',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sent_date', models.DateField(default=datetime.date.today)),
                ('req_sender', models.CharField(blank=True, max_length=200, null=True)),
                ('req_msg', models.CharField(blank=True, max_length=1000, null=True)),
                ('req_receiver', models.CharField(blank=True, max_length=200, null=True)),
                ('req_status', models.CharField(blank=True, max_length=200, null=True)),
                ('response_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 15, 11, 28, 32, 724590)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 15, 11, 28, 32, 733590)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 15, 11, 28, 32, 733590)),
        ),
    ]
