# Generated by Django 4.1 on 2022-10-08 15:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0195_feedfile_filename_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='iosfile',
            name='fileName',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='IOSFileComment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='IOSFileStatus',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 21, 28, 14, 453987)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 21, 28, 14, 489975)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 21, 28, 14, 490972)),
        ),
    ]
