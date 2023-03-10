# Generated by Django 4.1 on 2022-10-09 15:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0198_suricalguide_designuploaddate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suricalguide',
            name='tracking',
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='DispatchAddress',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='DispatchComment',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='DispatchDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='trackingId',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 9, 21, 20, 58, 90046)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 9, 21, 20, 58, 144677)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 9, 21, 20, 58, 144677)),
        ),
    ]
